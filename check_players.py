import sqlite3

def main():
    # データベースに接続
    conn = sqlite3.connect("players.db")
    cur = conn.cursor()

    # playersテーブルの内容をすべて取得
    cur.execute("SELECT * FROM players")
    rows = cur.fetchall()

    # 表示
    if rows:
        for row in rows:
            print(row)
    else:
        print("playersテーブルにデータがありません。")

    conn.close()

if __name__ == "__main__":
    main()