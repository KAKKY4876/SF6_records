from playwright.sync_api import sync_playwright
import sqlite3
import time
import os
from get_db import GetDB

def main():
    act_list, index = get_act_data()
    player_list = GetDB.get_players()

    for player in player_list:
        get_battle_logs(player, act_list, index)


def get_act_data():
    act_list = GetDB.get_act_list()
    index = len(act_list) - 1
    return act_list, index


def get_personal_logs(player):
    act_list, index = get_act_data()
    get_battle_logs(player, act_list, index)


def get_battle_logs(player, act_list, index):
    act = act_list[index]  # 指定されたインデックスのアクトデータを取得
    included_old = False  # 古いデータが含まれたかどうかを追跡するフラグ
    startline = act["startline"]  # アクト開始日時をパース
    deadline = act["deadline"]  # アクト終了日時をパース
    db_dir = f"players/{player}/{act['act']}"
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "battle_logs.db")  # バトルログを保存するSQLiteデータベースのパスを設定
    end = False  # ループを終了するかどうかを示すフラグ
    new_battle_logs = []  # 新しく取得したバトルログを格納するリスト

    if os.path.exists(db_path):  # 既存のバトルログデータベースが存在するかチェック
        firstTime = False  # ファイルが存在する場合、初回処理ではない
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS battle_logs (
                id INTEGER PRIMARY KEY,
                replay_id TEXT UNIQUE,
                date TEXT,
                match TEXT,
                p1_league_point TEXT,
                p1_master_rating TEXT,
                p1_name TEXT,
                p1_player_id TEXT,
                p1_type TEXT,
                p1_character TEXT,
                p1_result TEXT,
                p2_league_point TEXT,
                p2_master_rating TEXT,
                p2_name TEXT,
                p2_player_id TEXT,
                p2_type TEXT,
                p2_character TEXT,
                p2_result TEXT
            )''')
            cursor.execute('SELECT replay_id FROM battle_logs ORDER BY date DESC LIMIT 1')
            existing = cursor.fetchone()
            existing_id = existing[0] if existing else None  # 既存の最新リプレイIDを取得
    else:  # データベースが存在しない場合
        firstTime = True  # 初回処理
        existing_id = None

    with sync_playwright() as p:  # Playwrightを使用してブラウザを自動制御
        browser = p.chromium.launch(headless=False)  # Chromiumブラウザを起動（ヘッドレスモード）
        context = browser.new_context(  # 認証情報とカスタムユーザーエージェントを設定してコンテキストを作成
            storage_state="auth.json",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
        )
        page = context.new_page()  # ページオブジェクトを作成

        for _ in range(10000):
            try:
                page.goto(
                    f"https://www.streetfighter.com/6/buckler/ja-jp/profile/{player}/",
                    wait_until="domcontentloaded",
                    timeout=60000
                )
                break
            except Exception as e:
                print("retry:", e)
                time.sleep(3)
        
        i = 0  # ページ番号のカウント
        while i <= 10:  # ページをループして全バトルログを取得
            i += 1
            if i == 1:  # 最初のページは直接アクセスしているため、URLに"battlelog.json"が含まれない
                with page.expect_response(lambda r: "battlelog.json" in r.url, timeout=10000) as res_info: # レスポンスを待機（URLに"battlelog.json"を含むもの）
                    body = page.locator("body")  # ページのボディ要素を取得
                    page.locator("div.profile_nav_inner__UWe8e li:nth-of-type(3)").click()  # BATTLE LOGのタブをクリック
                    page.wait_for_load_state("networkidle")  # ページが完全に読み込まれるまで待機
            else:  # 2ページ目以降はURLに"battlelog.json"が含まれるため、直接待機
                with page.expect_response(lambda r: "battlelog.json" in r.url, timeout=10000) as res_info: # レスポンスを待機（URLに"battlelog.json"を含むもの）
                    body = page.locator("body")  # ページのボディ要素を取得
                    next_btn = body.locator("li.next")  # 次ページボタンを取得
                    next_btn.click()  # 次ページに移動
                    page.wait_for_function(f"""
                    () => {{
                    const el = document.querySelector('li.active');
                    return el && el.textContent.trim() === "{i}";
                    }}
                    """)
                if page.locator("li.next.disabled").count() > 0:  # 次ページボタンが無効な場合（ラスト）
                    end = True  # ループを終了
            response = res_info.value # レスポンスを取得
            data = response.json() # JSONデータを取得
            replay_list = data["pageProps"]["replay_list"]  # バトルログのリストを取得
            rows = len(replay_list)  # 現在のページのバトルログ行数を取得
            if rows == 0:  # バトルログが存在しない場合
                end = True  # ループを終了
                break  # ループを終了

            for j in range(rows):  # 各バトルログ行をループして処理
                battle = replay_list[j]  # 指定したバトルデータを取得

                replay_id = battle["replay_id"]  # リプレイIDを取得
                dt = battle["uploaded_at"]  # バトル日時を取得
                match = battle["replay_battle_type_name"]  # マッチ情報を取得
                if firstTime == False and replay_id == existing_id:  # 既存IDと同じ場合は重複を避ける
                    end = True  # ループを終了
                    break

                p1Data = battle["player1_info"]  # プレイヤー1のデータを取得
                league_point1 = p1Data["league_point"]  # プレイヤー1のLPを取得
                master_rating1 = p1Data["master_rating"]  # プレイヤー1のマスターポイントを取得
                name1 = p1Data["player"]["fighter_id"]  # プレイヤー1の名前を取得
                player_id1 = p1Data["player"]["short_id"]  # プレイヤー1のIDを取得
                round_results1 = str(p1Data["round_results"])  # プレイヤー1のラウンド結果を取得
                character1 = p1Data["character_name"]  # プレイヤー1の使用キャラクターを取得
                text = p1Data["battle_input_type_name"]  # プレイヤー1のタイプを取得
                if "クラシック" in text:
                    type1 = "C"
                elif "モダン" in text:
                    type1 = "M"
                else:
                    type1 = "D"
                
                p2Data = battle["player2_info"]  # プレイヤー2のデータを取得
                league_point2 = p2Data["league_point"]  # プレイヤー2のLPを取得
                master_rating2 = p2Data["master_rating"]  # プレイヤー2のマスターポイントを取得
                name2 = p2Data["player"]["fighter_id"]  # プレイヤー2の名前を取得
                player_id2 = p2Data["player"]["short_id"]  # プレイヤー2のIDを取得
                round_results2 = str(p2Data["round_results"])  # プレイヤー2のラウンド結果を取得
                character2 = p2Data["character_name"]  # プレイヤー2の使用キャラクターを取得
                text = p2Data["battle_input_type_name"]  # プレイヤー2のタイプを取得
                if "クラシック" in text:
                    type2 = "C"
                elif "モダン" in text:
                    type2 = "M"
                else:
                    type2 = "D"

                if dt < startline:  # バトル日時がアクト開始前の場合
                    included_old = True  # 古いデータフラグを立てる
                    end = True  # ループを終了
                    break
                elif dt <= deadline:  # バトル日時がアクト期間内の場合
                    battle_log = {  # バトルログの辞書構造を作成
                        "replay_id": replay_id,
                        "date": dt,
                        "match": match,
                        "p1": {
                            "league_point": league_point1,
                            "master_rating": master_rating1,
                            "name": name1,
                            "player_id": player_id1,
                            "type": type1,
                            "character": character1,
                            "result": round_results1
                        },
                        "p2": {
                            "league_point": league_point2,
                            "master_rating": master_rating2,
                            "name": name2,
                            "player_id": player_id2,
                            "type": type2,
                            "character": character2,
                            "result": round_results2
                        }
                    }
                    new_battle_logs.append(battle_log)  # 新しいバトルログをリストに追加
            if end:  # ループ終了条件を確認
                break

        browser.close()  # ブラウザを閉じる

    new_battle_logs.reverse()  # 新しいバトルログを年代順にソート

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS battle_logs (
        id INTEGER PRIMARY KEY,
        replay_id TEXT UNIQUE,
        date TEXT,
        match TEXT,
        p1_league_point TEXT,
        p1_master_rating TEXT,
        p1_name TEXT,
        p1_player_id TEXT,
        p1_type TEXT,
        p1_character TEXT,
        p1_result TEXT,
        p2_league_point TEXT,
        p2_master_rating TEXT,
        p2_name TEXT,
        p2_player_id TEXT,
        p2_type TEXT,
        p2_character TEXT,
        p2_result TEXT
    )''')
    for battle_log in new_battle_logs:
        cursor.execute('''INSERT OR IGNORE INTO battle_logs (
            replay_id, date, match,
            p1_league_point, p1_master_rating, p1_name, p1_player_id, p1_type, p1_character, p1_result,
            p2_league_point, p2_master_rating, p2_name, p2_player_id, p2_type, p2_character, p2_result
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            battle_log["replay_id"], battle_log["date"], battle_log["match"],
            battle_log["p1"]["league_point"], battle_log["p1"]["master_rating"], battle_log["p1"]["name"], battle_log["p1"]["player_id"], battle_log["p1"]["type"], battle_log["p1"]["character"], battle_log["p1"]["result"],
            battle_log["p2"]["league_point"], battle_log["p2"]["master_rating"], battle_log["p2"]["name"], battle_log["p2"]["player_id"], battle_log["p2"]["type"], battle_log["p2"]["character"], battle_log["p2"]["result"]
        ))
    conn.commit()
    conn.close()

    # デバッグ用出力
    for battle_log in new_battle_logs:
        print(battle_log["replay_id"])
        print(battle_log["date"])
        print(battle_log["match"])
        print(battle_log["p1"]["league_point"], battle_log["p1"]["master_rating"], battle_log["p1"]["name"], battle_log["p1"]["player_id"], battle_log["p1"]["type"], battle_log["p1"]["character"], battle_log["p1"]["result"])
        print(battle_log["p2"]["league_point"], battle_log["p2"]["master_rating"], battle_log["p2"]["name"], battle_log["p2"]["player_id"], battle_log["p2"]["type"], battle_log["p2"]["character"], battle_log["p2"]["result"])
        print("")

    if included_old:  # 古いデータが含まれた場合
        get_battle_logs(player, act_list, index - 1)  # 前のアクトのデータも取得（再帰呼び出し）

if __name__ == "__main__":
    main()