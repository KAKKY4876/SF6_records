from fastapi import FastAPI
import sqlite3
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/battle_logs")
def get_battlelogs():

    conn = sqlite3.connect("11/battle_logs.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM battle_logs ORDER BY date DESC")

    rows = cur.fetchall()

    conn.close()

    return rows

@app.get("/", response_class=HTMLResponse)
def index():

    with open("index.html", encoding="utf-8") as f:
        return f.read()