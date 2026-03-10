import sys
import os
import urllib.parse
import io
import sqlite3

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

form = {} # 辞書を初期化
content_length = os.environ.get('CONTENT_LENGTH') # 入力データ長を取得
if content_length: # 入力データがある場合
    body = sys.stdin.read(int(content_length)) # 入力データを標準入力から読み込み
    params = body.split('&') # 入力データを & で分割
    for param in params: # 分割されたデータを順に処理
        key, value = param.split('=') # 分割データを = で分割
        form[key] = urllib.parse.unquote(value) # キーと値を辞書に登録（値はURLデコードする）

param_str = form.get('param1', '') # ブラウザから送信されたparam1の値を辞書から取得

db_path = "bookdb.db"			# データベースファイル名を指定
con = sqlite3.connect(db_path)	# データベースに接続
con.row_factory = sqlite3.Row	# 属性名で値を取り出せるようにする
cur = con.cursor()				# カーソルを取得

print("Content-type: text/html; charset=utf-8\r\n")
print("")
print(f'''
<html>
    <body style="background-color:#EFDEC0;">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <div style="text-align:center; font-size:40px; font-weight:bold; margin:20px;">
            <b>
                書籍を検索
            </b>
        </div>

        <div style="text-align:center; font-size:40px; font-weight:bold; margin:20px;">
            <form name="form1" action="/cgi-bin/report2_search.py" method="GET" style="display:inline-block;">
                <button type="submit" name="submit" style="width: 200px; height: 30px;">
                    書籍を検索
                </button>
            </form>

            <form name="form1" action="/cgi-bin/report2_add.py" method="GET" style="display:inline-block;">
                <button type="submit" name="submit" style="width: 200px; height: 30px;">
                    書籍を追加
                </button>
            </form>
            <img src="/shelf.jpg" style="width:20%; height:auto; display:block; margin:0 auto;">
        </div>
        <div style="width: 900px; margin: 0 auto; text-align: center;">
            <form name="form1" action="/cgi-bin/report2_search.py" method="POST">
                <input type="text" name="param1" style="width: 400px" value="{param_str}">
                <button type="submit" name="submit" style="width: 100px">
                    検索
                </button>
            </form>
        </div>
''')
if param_str == "":
    con.commit()
    con.close()
    print("""
    </body>
</html>
    """)
    sys.exit()

try:
    cur.execute("SELECT * FROM BOOKLIST WHERE TITLE LIKE ? OR AUTHOR LIKE ? OR PUBLISHER LIKE ?",('%' + param_str + '%', '%' + param_str + '%', '%' + param_str + '%'))
    rows = cur.fetchall()		# 検索結果をリストとして取得
    print(f'''
        <div style="text-align:center; font-size:40px; font-weight:bold; margin:20px 0;">
            "{param_str}" の検索結果一覧
        </div>
        <br>
    ''')
    if not rows:
        print('''
        <br>
        <div style="text-align: center; font-size:20px;">
            見つかりませんでした。
        </div>
        ''')
    else:
        print('''
        <div style="text-align:center;">
            <table bgcolor="#778CA3" cellspacing="1" style="margin-left:auto; margin-right:auto;" border-collapse: collapse; border="1" cellpadding="10">
                <tr style='color:white; margin: 0 auto; text-align: center;'>
                    <th width='50'>
                        ID
                    </th>
                    <th width='500'>
                        タイトル
                    </th>
                    <th width='100'>
                        著者
                    </th>
                    <th width='150'>
                        出版社
                    </th>
                    <th width='50'>
                        価格
                    </th>
                    <th width='100'>
                        ISBN
                    </th>
                    <th width='100'>
                    </th>

                </tr>
        ''')
        for row in rows:
            print(f'''
                <tr style="background-color:#E9FAF9; margin: 0 auto; text-align: center;">
                    <td>{row["ID"]}</td>
                    <td>{row["TITLE"]}</td>
                    <td>{row["AUTHOR"]}</td>
                    <td>{row["PUBLISHER"]}</td>
                    <td>{row["PRICE"]}</td>
                    <td>{row["ISBN"]}</td>
                    <td>
                        <form name="form1" action="/cgi-bin/report2_edit.py" method="POST">
                            <input type="hidden" name="param1" value="{param_str}">
                            <button type="submit" name="id" style="width: 100px" value="{row["ID"]}">
                                編集
                            </button>
                        </form>
                    </td>
                </tr>
            ''')

        print("</table>")
        print("</div>")

except sqlite3.Error as e:		# エラー処理
    print("Error occurred:", e.args[0])

con.commit()
con.close()
print("</body>")
print("</html>")

#py -m http.server --cgi 8000