import sqlite3
import json
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from get_db import GetDB

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/battle_logs/{player_id}")
def get_battlelogs(player_id: str):

    db_path = f"players/{player_id}/{GetDB.get_recent_act()}/battle_logs.db"

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT
        replay_id,
        date,
        match,
        p1_league_point,
        p1_master_rating,
        p1_name,
        p1_player_id,
        p1_type,
        p1_character,
        p1_result,
        p2_league_point,
        p2_master_rating,
        p2_name,
        p2_player_id,
        p2_type,
        p2_character,
        p2_result
        FROM battle_logs
        ORDER BY date DESC
    """)

    rows = cur.fetchall()

    conn.close()

    battle_logs = []

    for row in rows:

        p1_result = json.loads(row[9])
        p2_result = json.loads(row[16])
        
        if row[6] == player_id:
            win_count = sum(1 for x in p1_result if x != 0)
        elif row[13] == player_id:
            win_count = sum(1 for x in p2_result if x != 0)
        else:
            continue

        if win_count >= 2:
            win_or_lose = True
        else:
            win_or_lose = False

        battle_logs.append({
            "replay_id": row[0],
            "date": row[1],
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

    if player_id == battle_logs[-1]["p1_player_id"]:
        player_name = battle_logs[-1]["p1_name"] if battle_logs else "Unknown Player"
    else:
        player_name = battle_logs[-1]["p2_name"] if battle_logs else "Unknown Player"

    return {
        "player_name": player_name,
        "battle_logs": battle_logs
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

