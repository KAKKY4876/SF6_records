from playwright.sync_api import sync_playwright
from datetime import datetime
import time
import os
import sqlite3

# 保存先のSQLiteデータベースパス
db_path = os.path.join("act.db")
window_check = False

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS acts (
            act INTEGER PRIMARY KEY,
            startline TEXT,
            deadline TEXT
        )
    ''')
    cursor.execute('SELECT act FROM acts ORDER BY act DESC LIMIT 1')
    recent = cursor.fetchone()
    recent_act = recent[0] if recent else None  # 既存の最新ACTを取得

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
                "https://www.streetfighter.com/6/buckler/ja-jp/reward/fightingpass",
                wait_until="domcontentloaded",
                timeout=60000
            )
            break
        except Exception as e:
            print("retry:", e)
            time.sleep(3)

    with page.expect_response(lambda r: "api/masterpass" in r.url, timeout=10000) as res_info: # レスポンスを待機（URLに"battlelog.json"を含むもの）
        page.locator("aside.reward_nav_reward_nav__FykFd li:nth-of-type(4)").click()  # BATTLE LOGのタブをクリック
        page.wait_for_load_state("networkidle")  # ページが完全に読み込まれるまで待機
    response = res_info.value # レスポンスを取得
    data = response.json() # JSONデータを取得
    masterpass = data["messageList"]["master_rate_pass_list"][0] # アクティベーションのデータを取得
    act = masterpass["season_id"] # アクティベーション番号
    startline = int(masterpass["start_at"])
    deadline = int(masterpass["end_at"])
    browser.close()

if act > recent_act:
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT OR REPLACE INTO acts (act, startline, deadline) VALUES (?, ?, ?)",
                    (act, startline, deadline))
        conn.commit()