import sqlite3  # SQLiteデータベース操作用
import json  # JSON形式のデータ処理用
import os
from datetime import datetime, timezone, timedelta  # 日時処理用
from typing import Optional  # 型ヒント用

from fastapi import FastAPI  # FastAPIフレームワーク
from fastapi.staticfiles import StaticFiles  # 静的ファイル提供用
from fastapi.responses import HTMLResponse  # HTML応答返却用
from get_db import GetDB  # データベース取得用カスタムモジュール

app = FastAPI()  # FastAPIアプリケーション初期化
app.mount("/static", StaticFiles(directory="static"), name="static")  # 静的ファイルディレクトリマウント

@app.get("/battle_logs/{player_id}/{act}")  # バトルログ取得エンドポイント定義
def get_battlelogs(  # バトルログ取得関数
    player_id: str,  # プレイヤーID
    act: str,  # アクト番号
    away_character_id: Optional[str] = None,  # 相手キャラクターID(オプション)
    away_input_type_id: Optional[str] = None,  # 相手入力タイプID(オプション)
    battle_type_id: Optional[str] = None,  # バトルタイプID(オプション)
    home_character_id: Optional[str] = None,  # 自分キャラクターID(オプション)
    home_input_type_id: Optional[str] = None,  # 自分入力タイプID(オプション)
    played_from: Optional[str] = None,  # プレイ開始日時(オプション)
    played_to: Optional[str] = None,  # プレイ終了日時(オプション)
    page: int = 1,  # ページ番号(デフォルト1)
):

    db_path = f"players/{player_id}/{act}/battle_logs.db"  # データベースパス生成

    conn = sqlite3.connect(db_path)  # データベース接続
    cur = conn.cursor()  # カーソル取得

    limit = 20  # 1ページあたりの件数設定

    jst = timezone(timedelta(hours=9))  # 日本標準時(JST)タイムゾーン設定

    if not played_from:  # 開始日時未指定の場合
        played_from = "1970-01-01T00:00:00"  # エポック時刻を開始日時に設定
    if not played_to:  # 終了日時未指定の場合
        played_to = datetime.now(jst).strftime("%Y-%m-%d") + "T23:59:59"  # 今日の日付の23:59:59に設定

    dt_from = datetime.strptime(played_from, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=jst)  # 開始日時をdatetime形式に変換
    dt_to = datetime.strptime(played_to, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=jst) + timedelta(days=1) - timedelta(seconds=1)  # 終了日時をdatetime形式に変換

    from_ts = int(dt_from.timestamp())  # 開始日時をタイムスタンプに変換
    to_ts = int(dt_to.timestamp())  # 終了日時をタイムスタンプに変換

    # バトルログ取得SQLクエリ定義
    query = """
            SELECT
            replay_id, date, match,
            p1_league_point, p1_master_rating, p1_name, p1_player_id, p1_type, p1_character, p1_result,
            p2_league_point, p2_master_rating, p2_name, p2_player_id, p2_type, p2_character, p2_result
            FROM battle_logs
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
            """

    cur.execute(query, (from_ts, to_ts))  # SQL実行(期間内のバトルログ取得)
    rows = cur.fetchall()  # 全行を取得
    conn.close()  # データベース接続を閉じる

    battle_logs = []  # バトルログリスト初期化

    for row in rows:  # 各バトルログ行をループ処理

        p1_result = json.loads(row[9])  # プレイヤー1の結果をJSON形式から辞書に変換
        p2_result = json.loads(row[16])  # プレイヤー2の結果をJSON形式から辞書に変換

        if row[6] == player_id:  # 対象プレイヤーがプレイヤー1の場合
            win_count = sum(1 for x in p1_result if x != 0)  # 勝利数をカウント
            if home_input_type_id and row[7] != home_input_type_id:  # 自分入力タイプフィルタ(条件不一致時)
                continue  # 次のループへ
            if home_character_id and row[8] != home_character_id:  # 自分キャラフィルタ(条件不一致時)
                continue  # 次のループへ
            if away_input_type_id and row[14] != away_input_type_id:  # 相手入力タイプフィルタ(条件不一致時)
                continue  # 次のループへ
            if away_character_id and row[15] != away_character_id:  # 相手キャラフィルタ(条件不一致時)
                continue  # 次のループへ
        elif row[13] == player_id:  # 対象プレイヤーがプレイヤー2の場合
            win_count = sum(1 for x in p2_result if x != 0)  # 勝利数をカウント
            if home_input_type_id and row[14] != home_input_type_id:  # 相手入力タイプフィルタ(条件不一致時)
                continue  # 次のループへ
            if home_character_id and row[15] != home_character_id:  # 相手キャラフィルタ(条件不一致時)
                continue  # 次のループへ            
            if away_input_type_id and row[7] != away_input_type_id:  # 自分入力タイプフィルタ(条件不一致時)
                continue  # 次のループへ
            if away_character_id and row[8] != away_character_id:  # 自分キャラフィルタ(条件不一致時)
                continue  # 次のループへ
        else:  # 対象プレイヤーが見つからない場合
            continue  # 次のループへ
        if battle_type_id and row[2] != battle_type_id:  # バトルタイプフィルタ(条件不一致時)
            continue  # 次のループへ

        win_or_lose = win_count >= 2  # 2勝以上で勝利判定(True/False)

        battle_logs.append({  # バトルログを辞書形式で追加
            "replay_id": row[0],  # リプレイID
            "date": datetime.fromtimestamp(int(row[1]) + 32400).strftime("%Y-%m-%d %H:%M:%S"),  # 試合日時
            "match": row[2],  # マッチタイプ
            "p1_league_point": row[3],  # プレイヤー1リーグポイント
            "p1_master_rating": row[4],  # プレイヤー1マスターレーティング
            "p1_name": row[5],  # プレイヤー1名前
            "p1_player_id": row[6],  # プレイヤー1ID
            "p1_type": row[7],  # プレイヤー1入力タイプ
            "p1_character": row[8],  # プレイヤー1キャラクター
            "p1_result": p1_result,  # プレイヤー1試合結果
            "p2_league_point": row[10],  # プレイヤー2リーグポイント
            "p2_master_rating": row[11],  # プレイヤー2マスターレーティング
            "p2_name": row[12],  # プレイヤー2名前
            "p2_player_id": row[13],  # プレイヤー2ID
            "p2_type": row[14],  # プレイヤー2入力タイプ
            "p2_character": row[15],  # プレイヤー2キャラクター
            "p2_result": p2_result,  # プレイヤー2試合結果
            "win_or_lose": win_or_lose  # 勝利/敗北判定
        })

    if battle_logs:  # バトルログが存在する場合
        if player_id == battle_logs[0]["p1_player_id"]:  # プレイヤーがプレイヤー1か判定
            player_name = battle_logs[0]["p1_name"]  # プレイヤー1名前を取得
        else:  # プレイヤーがプレイヤー2の場合
            player_name = battle_logs[0]["p2_name"]  # プレイヤー2名前を取得
    else:  # バトルログが存在しない場合
        player_name = "Unknown Player"  # デフォルト名前を設定

    total_pages = (len(battle_logs) + limit - 1) // limit  # 総ページ数を計算
    start_index = limit * (page - 1)  # ページの開始インデックスを計算
    end_index = limit * page  # ページの終了インデックスを計算
    battle_logs_page = battle_logs[start_index:end_index]  # 該当ページのバトルログを抽出

    acts = [name for name in os.listdir(f"players/{player_id}") if os.path.isdir(os.path.join(f"players/{player_id}", name))]

    return {  # 結果を辞書形式で返却
        "player_name": player_name,  # プレイヤー名
        "acts": acts,  # プレイヤーのアクトフォルダリスト
        "battle_logs": battle_logs_page,  # 該当ページのバトルログ
        "page": page,  # 現在のページ番号
        "total_pages": total_pages,  # 総ページ数
        "recent_act": act  # 最新アクト番号
    }

@app.get("/", response_class=HTMLResponse)  # ルートエンドポイント定義
def index():  # インデックスページ取得関数
    with open("templates/index.html", encoding="utf-8") as f:  # HTMLテンプレートファイルを開く
        html = f.read()  # ファイル内容を読み込む

    html = html.replace("{act}", str(GetDB.get_recent_act()))  # 最新アクト番号をテンプレートに埋め込み

    return html  # HTMLを返却

@app.get("/{player_id}/{act}/battle_logs", response_class=HTMLResponse)  # プレイヤーページエンドポイント定義
def player_page(player_id: str, act: str):  # プレイヤーページ取得関数

    with open("templates/battle_logs.html", encoding="utf-8") as f:  # バトルログテンプレートファイルを開く
        html = f.read()  # ファイル内容を読み込む

    html = html.replace("{act}", act)  # アクト番号をテンプレートに埋め込み
    html = html.replace("{player_id}", player_id)  # プレイヤーIDをテンプレートに埋め込み

    return html  # HTMLを返却



"""
    py -m uvicorn main:app --reload
"""

"""
    git add .
    git commit -m ""
    git push
"""

