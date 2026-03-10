import sqlite3
from pathlib import Path

def print_battle_stats_db():

    act = input("actを入力してください: ")
    path = Path(act) / "battle_stats.db"
    if not path.exists():
        print(f"DBが見つかりません: {path}")
        return

    with sqlite3.connect(str(path)) as conn:
        cur = conn.cursor()

        # テーブル確認
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        if "battle_stats" not in tables:
            print("テーブル `battle_stats` が存在しません。b.py を実行してデータ生成を確認してください。")
            return

        # スキーマ出力
        print("== battle_stats schema ==")
        cur.execute("PRAGMA table_info(battle_stats)")
        for row in cur.fetchall():
            # (cid, name, type, notnull, dflt_value, pk)
            print(f"  {row[1]} ({row[2]})")
        print()

        # データ出力
        cur.execute("SELECT * FROM battle_stats ORDER BY date DESC")
        rows = cur.fetchall()
        if not rows:
            print("battle_stats テーブルに行が存在しません。")
            return

        print(f"== {len(rows)} rows in battle_stats (latest first) ==")
        colnames = [c[0] for c in cur.description]

        for r in rows:
            item = dict(zip(colnames, r))
            print("-- battle_stat --")
            for key, value in item.items():
                print(f"{key}: {value}")
            print("---")

if __name__ == "__main__":
    print_battle_stats_db()