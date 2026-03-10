import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("act.db")

def print_act_db(path=DB_PATH):
    if not path.exists():
        print(f"DB が見つかりません: {path}")
        return

    with sqlite3.connect(path) as conn:
        cur = conn.cursor()

        # テーブル存在確認
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='acts'")
        if cur.fetchone() is None:
            print("テーブル 'acts' が存在しません。act.json から import を確認してください。")
            return

        # スキーマ表示
        cur.execute("PRAGMA table_info(acts)")
        print("== acts schema ==")
        for col in cur.fetchall():
            print(f"  {col[1]} ({col[2]})")
        print()

        # データ表示
        cur.execute("SELECT act, startline, deadline FROM acts ORDER BY act")
        rows = cur.fetchall()
        if not rows:
            print("acts テーブルにデータがありません。")
            return

        print(f"== {len(rows)} rows ==")
        for act, startline, deadline in rows:
            try:
                start_dt = datetime.fromtimestamp(int(startline))
                deadline_dt = datetime.fromtimestamp(int(deadline))
                print(f"act={act} startline={startline} ({start_dt}) deadline={deadline} ({deadline_dt})")
            except Exception:
                print(f"act={act} startline={startline} deadline={deadline}")
        print("完了")

if __name__ == "__main__":
    print_act_db()