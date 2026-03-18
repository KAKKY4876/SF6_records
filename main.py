import sqlite3
import json
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from get_db import GetDB

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/battle_logs/{player_id}")
def get_battlelogs(
    player_id: str,
    away_character_id: Optional[str] = None,
    away_input_type_id: Optional[str] = None,
    battle_type_id: Optional[str] = None,
    home_character_id: Optional[str] = None,
    home_input_type_id: Optional[str] = None,
    played_from: Optional[str] = None,
    played_to: Optional[str] = None,
    page: int = 1,
):

    db_path = f"players/{player_id}/{GetDB.get_recent_act()}/battle_logs.db"

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    limit = 20
    offset = (page - 1) * limit

    jst = timezone(timedelta(hours=9))

    # If any query params are missing, apply safe defaults so this endpoint can be called
    # with only ?page=... (used by frontend JS) or from the form.
    if not played_from:
        played_from = "1970-01-01T00:00:00"
    if not played_to:
        played_to = datetime.now(jst).strftime("%Y-%m-%d") + "T23:59:59"  # 今日の日付の23:59:59に設定

    dt_from = datetime.strptime(played_from, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=jst)
    dt_to = datetime.strptime(played_to, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=jst) + timedelta(days=1) - timedelta(seconds=1)

    from_ts = int(dt_from.timestamp())
    to_ts = int(dt_to.timestamp())

    # まずは日付範囲の全件を取得し、Python側でフィルタリングしてページングします。
    # （要求: DBから全情報を取ってJSON化してから条件を絞る）
    query = """
            SELECT
            replay_id, date, match,
            p1_league_point, p1_master_rating, p1_name, p1_player_id, p1_type, p1_character, p1_result,
            p2_league_point, p2_master_rating, p2_name, p2_player_id, p2_type, p2_character, p2_result
            FROM battle_logs
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
            """

    cur.execute(query, (from_ts, to_ts))
    rows = cur.fetchall()
    conn.close()

    battle_logs = []

    for row in rows:

        p1_result = json.loads(row[9])
        p2_result = json.loads(row[16])

        if row[6] == player_id:
            win_count = sum(1 for x in p1_result if x != 0)
            if home_input_type_id and row[7] != home_input_type_id:
                continue
            if home_character_id and row[8] != home_character_id:
                continue
            if away_input_type_id and row[14] != away_input_type_id:
                continue
            if away_character_id and row[15] != away_character_id:
                continue
        elif row[13] == player_id:
            win_count = sum(1 for x in p2_result if x != 0)
            if home_input_type_id and row[14] != home_input_type_id:
                continue
            if home_character_id and row[15] != home_character_id:
                continue            
            if away_input_type_id and row[7] != away_input_type_id:
                continue
            if away_character_id and row[8] != away_character_id:
                continue
        else:
            continue
        if battle_type_id and row[2] != battle_type_id:
            continue

        win_or_lose = win_count >= 2

        battle_logs.append({
            "replay_id": row[0],
            "date": datetime.fromtimestamp(int(row[1]) + 32400).strftime("%Y-%m-%d %H:%M:%S"),
            "match": row[2],
            "p1_league_point": row[3],
            "p1_master_rating": row[4],
            "p1_name": row[5],
            "p1_player_id": row[6],
            "p1_type": row[7],
            "p1_character": row[8],
            "p1_result": p1_result,
            "p2_league_point": row[10],
            "p2_master_rating": row[11],
            "p2_name": row[12],
            "p2_player_id": row[13],
            "p2_type": row[14],
            "p2_character": row[15],
            "p2_result": p2_result,
            "win_or_lose": win_or_lose
        })

    if battle_logs:
        if player_id == battle_logs[0]["p1_player_id"]:
            player_name = battle_logs[0]["p1_name"]
        else:
            player_name = battle_logs[0]["p2_name"]
    else:
        player_name = "Unknown Player"

    total_pages = (len(battle_logs) + limit - 1) // limit

    # ページング: nページに20*(n-1)番目から20*n番目の要素を返す
    start_index = 20 * (page - 1)
    end_index = 20 * page
    battle_logs_page = battle_logs[start_index:end_index]

    return {
        "player_name": player_name,
        "battle_logs": battle_logs_page,
        "page": page,
        "total_pages": total_pages
    }

@app.get("/", response_class=HTMLResponse)
def index():
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()
    

@app.get("/{player_id}/battle_logs", response_class=HTMLResponse)
def player_page(player_id: str):

    with open("templates/battle_logs.html", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{player_id}", player_id)

    return html



"""
    py -m uvicorn main:app --reload
"""

"""
    git add .
    git commit -m ""
    git push
"""

