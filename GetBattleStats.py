from playwright.sync_api import sync_playwright
from datetime import date
import time
import sqlite3
import os

# 対象のアクティベーション番号（フォルダ名）
act = "11"
# 保存先のSQLiteデータベースパス
db_path = os.path.join(act, "battle_stats.db")
window_check = False

with sync_playwright() as p:  # Playwrightを使用してブラウザを自動制御
    browser = p.chromium.launch(headless=window_check)  # Chromiumブラウザを起動（ヘッドレスモード）
    context = browser.new_context(  # 認証情報とカスタムユーザーエージェントを設定してコンテキストを作成
        storage_state="auth.json",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    )
    page = context.new_page()  # ページオブジェクトを作成

    for _ in range(10000):
        try:
            page.goto(
                "https://www.streetfighter.com/6/buckler/ja-jp/profile/3396222654/",
                wait_until="domcontentloaded",
                timeout=60000
            )
            break
        except Exception as e:
            print("retry:", e)
            time.sleep(3)

    with page.expect_response(lambda r: "play.json" in r.url, timeout=10000) as res_info: # レスポンスを待機（URLに"battlelog.json"を含むもの）
        page.locator("div.profile_nav_inner__UWe8e li:nth-of-type(2)").click()  # BATTLE LOGのタブをクリック
        page.wait_for_load_state("networkidle")  # ページが完全に読み込まれるまで待機

    response = res_info.value # レスポンスを取得
    data = response.json() # JSONデータを取得
    stats = data["pageProps"]["play"]["battle_stats"]  # バトルスタッツのデータを取得

    corner_time = stats["corner_time"]
    cornered_time = stats["cornered_time"]
    drive_impact = stats["drive_impact"]
    drive_impact_to_drive_impact = stats["drive_impact_to_drive_impact"]
    drive_parry = stats["drive_parry"]
    drive_reversal = stats["drive_reversal"]
    gauge_rate_ca = stats["gauge_rate_ca"]
    gauge_rate_drive_arts = stats["gauge_rate_drive_arts"]
    gauge_rate_drive_guard = stats["gauge_rate_drive_guard"]
    gauge_rate_drive_impact = stats["gauge_rate_drive_impact"]
    gauge_rate_drive_other = stats["gauge_rate_drive_other"]
    gauge_rate_drive_reversal = stats["gauge_rate_drive_reversal"]
    gauge_rate_drive_rush_from_cancel = stats["gauge_rate_drive_rush_from_cancel"]
    gauge_rate_drive_rush_from_parry = stats["gauge_rate_drive_rush_from_parry"]
    gauge_rate_sa_lv1 = stats["gauge_rate_sa_lv1"]
    gauge_rate_sa_lv2 = stats["gauge_rate_sa_lv2"]
    gauge_rate_sa_lv3 = stats["gauge_rate_sa_lv3"]
    just_parry = stats["just_parry"]
    punish_counter = stats["punish_counter"]
    received_drive_impact = stats["received_drive_impact"]
    received_drive_impact_to_drive_impact = stats["received_drive_impact_to_drive_impact"]
    received_punish_counter = stats["received_punish_counter"]
    received_stun = stats["received_stun"]
    received_throw_count = stats["received_throw_count"]
    received_throw_drive_parry = stats["received_throw_drive_parry"]
    stun = stats["stun"]
    throw_count = stats["throw_count"]
    throw_drive_parry = stats["throw_drive_parry"]
    throw_tech = stats["throw_tech"]

    browser.close()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS battle_stats (
    id INTEGER PRIMARY KEY,
    date TEXT UNIQUE,
    corner_time FLOAT,
    cornered_time FLOAT,
    drive_impact FLOAT,
    drive_impact_to_drive_impact FLOAT,
    drive_parry FLOAT,
    drive_reversal FLOAT,
    gauge_rate_ca FLOAT,
    gauge_rate_drive_arts FLOAT,
    gauge_rate_drive_guard FLOAT,
    gauge_rate_drive_impact FLOAT,
    gauge_rate_drive_other FLOAT,
    gauge_rate_drive_reversal FLOAT,
    gauge_rate_drive_rush_from_cancel FLOAT,
    gauge_rate_drive_rush_from_parry FLOAT,
    gauge_rate_sa_lv1 FLOAT,
    gauge_rate_sa_lv2 FLOAT,
    gauge_rate_sa_lv3 FLOAT,
    just_parry FLOAT,
    punish_counter FLOAT,
    received_drive_impact FLOAT,
    received_drive_impact_to_drive_impact FLOAT,
    received_punish_counter FLOAT,
    received_stun FLOAT,
    received_throw_count FLOAT,
    received_throw_drive_parry FLOAT,
    stun FLOAT,
    throw_count FLOAT,
    throw_drive_parry FLOAT,
    throw_tech FLOAT
)''')

# 現在の取得データを一行として保存
cursor.execute('''INSERT OR REPLACE INTO battle_stats (
    date,
    corner_time,
    cornered_time,
    drive_impact,
    drive_impact_to_drive_impact,
    drive_parry,
    drive_reversal,
    gauge_rate_ca,
    gauge_rate_drive_arts,
    gauge_rate_drive_guard,
    gauge_rate_drive_impact,
    gauge_rate_drive_other,
    gauge_rate_drive_reversal,
    gauge_rate_drive_rush_from_cancel,
    gauge_rate_drive_rush_from_parry,
    gauge_rate_sa_lv1,
    gauge_rate_sa_lv2,
    gauge_rate_sa_lv3,
    just_parry,
    punish_counter,
    received_drive_impact,
    received_drive_impact_to_drive_impact,
    received_punish_counter,
    received_stun,
    received_throw_count,
    received_throw_drive_parry,
    stun,
    throw_count,
    throw_drive_parry,
    throw_tech
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
    int(time.time()),  # 現在のUnixタイムスタンプ
    corner_time,
    cornered_time,
    drive_impact,
    drive_impact_to_drive_impact,
    drive_parry,
    drive_reversal,
    gauge_rate_ca,
    gauge_rate_drive_arts,
    gauge_rate_drive_guard,
    gauge_rate_drive_impact,
    gauge_rate_drive_other,
    gauge_rate_drive_reversal,
    gauge_rate_drive_rush_from_cancel,
    gauge_rate_drive_rush_from_parry,
    gauge_rate_sa_lv1,
    gauge_rate_sa_lv2,
    gauge_rate_sa_lv3,
    just_parry,
    punish_counter,
    received_drive_impact,
    received_drive_impact_to_drive_impact,
    received_punish_counter,
    received_stun,
    received_throw_count,
    received_throw_drive_parry,
    stun,
    throw_count,
    throw_drive_parry,
    throw_tech
))
conn.commit()
conn.close()