import sqlite3

try:
    # battle_logs.db に接続
    conn = sqlite3.connect('11/battle_logs.db')
    cursor = conn.cursor()

    # battle_logs テーブルが存在するかチェック
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='battle_logs'")
    if cursor.fetchone():
        # テーブルスキーマを確認
        cursor.execute("PRAGMA table_info(battle_logs)")
        columns = cursor.fetchall()
        print("テーブルスキーマ:")
        for col in columns:
            print(f"  {col[1]}: {col[2]}")
        print()
        
        # battle_logs テーブルから全てのデータを取得
        cursor.execute('SELECT * FROM battle_logs ORDER BY date DESC')
        rows = cursor.fetchall()

        if rows:
            # 各レコードを表示
            for row in rows:
                # タプルを辞書風に表示
                # カラム順序: id, replay_id, date, match, p1_league_point, p1_master_rating, p1_name, p1_player_id, p1_type, p1_character, p1_result, p2_league_point, p2_master_rating, p2_name, p2_player_id, p2_type, p2_character, p2_result
                print(f"ID: {row[0]}")
                print(f"  ReplayID: {row[1]}")
                print(f"  Date: {row[2]}")
                print(f"  Match: {row[3]}")
                print(f"  Player 1: {row[6]} (LP:{row[4]}, MR:{row[5]}, ID:{row[7]}) - Type:{row[8]} - {row[9]} - {row[10]}")
                print(f"  Player 2: {row[13]} (LP:{row[11]}, MR:{row[12]}, ID:{row[14]}) - Type:{row[15]} - {row[16]} - {row[17]}")
                print("  ---")
        else:
            print("battle_logs テーブルにデータがありません。")
    else:
        print("battle_logs テーブルが存在しません。GetBattleLog.py を実行してデータを作成してください。")

    # 接続を閉じる
    conn.close()

except sqlite3.Error as e:
    print(f"SQLite エラー: {e}")
except Exception as e:
    print(f"予期しないエラー: {e}")
