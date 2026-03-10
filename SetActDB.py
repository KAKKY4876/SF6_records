import json
import sqlite3
from pathlib import Path

ACT_JSON = Path("c:\\Users\\kakim\\Desktop\\SF6_records\\act.json")
ACT_DB = Path("c:\\Users\\kakim\\Desktop\\SF6_records\\act.db")

def init_act_db(path=ACT_DB):
    with sqlite3.connect(path) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS acts (
            act INTEGER PRIMARY KEY,
            startline INTEGER,
            deadline INTEGER
        )""")
        conn.commit()

def load_act_json(path=ACT_JSON):
    if not path.exists():
        raise FileNotFoundError(f"{path} が見つかりません")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_act_to_db(act_list, db_path=ACT_DB):
    init_act_db(db_path)
    with sqlite3.connect(db_path) as conn:
        sql = "INSERT OR REPLACE INTO acts (act, startline, deadline) VALUES (?, ?, ?)"
        params = [(a["act"], int(a["startline"]), int(a["deadline"])) for a in act_list]
        conn.executemany(sql, params)
        conn.commit()

def dump_act_db(db_path=ACT_DB):
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT act, startline, deadline FROM acts ORDER BY act").fetchall()
    print("act.db rows:", len(rows))
    for r in rows:
        print(r)

if __name__ == "__main__":
    act_data = load_act_json()
    save_act_to_db(act_data)
    dump_act_db()