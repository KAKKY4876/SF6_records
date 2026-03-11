import sqlite3

# ターミナルからIDの入力を取得
player_id = input("プレイヤーIDを入力してください: ")

# players.dbに接続
conn = sqlite3.connect("players.db")
cur = conn.cursor()

# playersテーブルが存在しない場合は作成
cur.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY
)
""")

# IDを保存
cur.execute("INSERT INTO players (id) VALUES (?)", (player_id,))

# 変更をコミット
conn.commit()

# 接続を閉じる
conn.close()

print(f"ID {player_id} をplayers.dbに保存しました。")