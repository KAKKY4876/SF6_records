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

title     = form.get('title', '')
author    = form.get('author', '')
publisher = form.get('publisher', '')
price     = form.get('price', '')
isbn      = form.get('isbn', '')

db_path = "bookdb.db"			# データベースファイル名を指定
con = sqlite3.connect(db_path)	# データベースに接続
cur = con.cursor()				# カーソルを取得

print("Content-type: text/html; charset=utf-8\r\n")
print("")
print('''
<html>
    <body style="background-color:#EFDEC0;">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <div style="text-align:center; font-size:40px; font-weight:bold; margin:20px;">
            <b>
                書籍を追加
            </b>
        </div>

        <div style="text-align:center; font-size:40px; font-weight:bold; margin:20px;">
            <form name="form1" action="/cgi-bin/report2_search.py" method="GET" style="display:inline-block;">
                <button style="width: 200px; height: 30px;">
                    書籍を検索
                </button>
            </form>

            <form name="form1" action="/cgi-bin/report2_add.py" method="GET" style="display:inline-block;">
                <button style="width: 200px; height: 30px;">
                    書籍を追加
                </button>
            </form>
        </div>
''')

if title == "" or author == "" or publisher == "" or price == "" or isbn == "":
    con.commit()
    con.close()
    print(f'''
        <div style="width: 900px; margin: 0 auto; text-align: center;">
            <form name="form1" action="/cgi-bin/report2_add.py" method="POST">
                <div>
                    <span style="display:inline-block; width:100px;">タイトル :</span>
                    <input type="text" name="title" style="width:400px;" value="{title}">
                </div>

                <div>
                    <span style="display:inline-block; width:100px;">著者 :</span>
                    <input type="text" name="author" style="width:400px;" value="{author}">
                </div>

                <div>
                    <span style="display:inline-block; width:100px;">出版社 :</span>
                    <input type="text" name="publisher" style="width:400px;" value="{publisher}">
                </div>

                <div>
                    <span style="display:inline-block; width:100px;">価格 :</span>
                    <input type="text" name="price" style="width:400px;" value="{price}">
                </div>

                <div>
                    <span style="display:inline-block; width:100px;">ISBN :</span>
                    <input type="text" name="isbn" style="width:400px;" value="{isbn}">
                </div>
                <br>
                <button type="submit" name="submit" style="width: 300px">
                    追加
                </button>
            </form>
        </div>
    </body>
</html>
    ''')
    sys.exit()

try:
    cur.execute("SELECT MAX(ID) FROM BOOKLIST")
    book_id = cur.fetchone()[0] + 1
    cur.execute("INSERT INTO BOOKLIST (ID, TITLE, AUTHOR, PUBLISHER, PRICE, ISBN) VALUES (?, ?, ?, ?, ?, ?)", (book_id, title, author, publisher, price, isbn))
    print(f'''
        <div style="width: 900px; margin: 0 auto; text-align: center;">
            書籍を以下の情報で追加しました
            <div>
                <span style="display:inline-block; width:100px;">ID :</span>
                {book_id}
            </div>

            <div>
                <span style="display:inline-block; width:100px;">タイトル :</span>
                {title}
            </div>

            <div>
                <span style="display:inline-block; width:100px;">著者 :</span>
                {author}
            </div>

            <div>
                <span style="display:inline-block; width:100px;">出版社 :</span>
                {publisher}
            </div>

            <div>
                <span style="display:inline-block; width:100px;">価格 :</span>
                {price}
            </div>

            <div>
                <span style="display:inline-block; width:100px;">ISBN :</span>
                {isbn}
            </div>
            <br>
            <form name="form1" action="/cgi-bin/report2_edit.py" method="POST" style="display:inline-block;">
                <input type="hidden" name="id" value="{book_id}">
                <button type="submit" name="mode" style="width: 200px" value="editting">
                    編集
                </button>
            </form>

            <form name="form1" action="/cgi-bin/report2_add.py" method="POST">
                <button type="submit" name="submit" style="width: 100px">
                    戻る
                </button>
            </form>
        </div>
    ''')


except sqlite3.Error as e:		# エラー処理
    print("Error occurred:", e.args[0])

con.commit()
con.close()
print("</body>")
print("</html>")