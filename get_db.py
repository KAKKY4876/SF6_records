import sqlite3

class GetDB:

    @staticmethod
    def get_players():
        conn = sqlite3.connect("players.db")
        cur = conn.cursor()

        cur.execute("SELECT id FROM players")
        rows = cur.fetchall()

        player_list = [row[0] for row in rows]

        conn.close()

        return player_list
    

    @staticmethod
    def get_act_list():
        with sqlite3.connect("act.db") as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT act, startline, deadline FROM acts ORDER BY act')
            rows = cursor.fetchall()

            act_list = [
                {"act": row[0], "startline": int(row[1]), "deadline": int(row[2])}
                for row in rows
            ]

        return act_list
    

    @staticmethod
    def get_recent_act():
        act_list = GetDB.get_act_list()
        return act_list[-1]["act"]