import sqlite3
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

    return rows


@app.get("/", response_class=HTMLResponse)
def index():
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()
    

@app.get("/{player_id}", response_class=HTMLResponse)
def player_page(player_id: str):

    with open("templates/player.html", encoding="utf-8") as f:
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

