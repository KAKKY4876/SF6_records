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

param_str = form.get('param1', '')
mode = form.get('mode', '')
book_id = form.get('id', '')

title = form.get('title', '')
author = form.get('author', '')
publisher = form.get('publisher', '')
price = form.get('price', '')
isbn = form.get('isbn', '')
if mode == 'edit' and (title == '' or author == '' or publisher == '' or price == '' or isbn == ''):
    mode = 'editting'

db_path = "bookdb.db"			# データベースファイル名を指定
con = sqlite3.connect(db_path)	# データベースに接続
con.row_factory = sqlite3.Row
cur = con.cursor()				# カーソルを取得

cur.execute("SELECT * FROM BOOKLIST WHERE ID = ?",(book_id,))
row = cur.fetchone() 

print("Content-type: text/html; charset=utf-8\r\n")
print("")
print('''
<html>
    <body style="background-color:#EFDEC0;">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <div style="text-align:center; font-size:40px; font-weight:bold; margin:20px;">
            <b>
                書籍を編集
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
try: 
    if mode == 'delete':
        cur.execute("DELETE FROM BOOKLIST WHERE ID = ?", (book_id,))
        con.commit()
        print(f'''
        <div style="text-align:center; font-size:40px; font-weight:bold; margin:20px;">
            <h>
                書籍を削除しました
            </h>
            <br>
            <form name="form1" action="/cgi-bin/report2_search.py" method="POST">
                <input type="hidden" name="param1" value="{param_str}">
                <button type="submit" name="submit" style="width: 100px">
                    戻る
                </button>
            </form>
        </div>
        ''')
        sys.exit()
    elif mode == 'editting':
        print(f'''
        <div style="width: 900px; margin: 0 auto; text-align: center;">
            <form name="form1" action="/cgi-bin/report2_edit.py" method="POST">
                <div>
                    <span style="display:inline-block; width:100px;">ID :</span>
                    {row["ID"]}
                </div>
                <div>
                    <span style="display:inline-block; width:100px;">タイトル :</span>
                    <input type="text" name="title" style="width:400px;" value="{row["TITLE"]}">
                </div>

                <div>
                    <span style="display:inline-block; width:100px;">著者 :</span>
                    <input type="text" name="author" style="width:400px;" value="{row["AUTHOR"]}">
                </div>

                <div>
                    <span style="display:inline-block; width:100px;">出版社 :</span>
                    <input type="text" name="publisher" style="width:400px;" value="{row["PUBLISHER"]}">
                </div>

                <div>
                    <span style="display:inline-block; width:100px;">価格 :</span>
                    <input type="text" name="price" style="width:400px;" value="{row["PRICE"]}">
                </div>

                <div>
                    <span style="display:inline-block; width:100px;">ISBN :</span>
                    <input type="text" name="isbn" style="width:400px;" value="{row["ISBN"]}">
                </div>
                <br>
                <input type="hidden" name="id" value="{row['ID']}">
                <input type="hidden" name="param1" value="{param_str}">
                <button type="submit" name="mode" style="width: 200px" value="edit">
                    編集
                </button>
            </form>
            <form name="form1" action="/cgi-bin/report2_edit.py" method="POST" style="display:inline-block;">
                <input type="hidden" name="param1" value="{param_str}">
                <button type="submit" name="id" style="width: 200px" value="{row['ID']}">
                    キャンセル
                </button>
            </form>
        </div>
        ''')
    elif mode == 'edit':
        cur.execute("UPDATE BOOKLIST SET TITLE = ?, AUTHOR = ?, PUBLISHER = ?, PRICE = ?, ISBN = ? WHERE ID = ?", (title, author, publisher, price, isbn, book_id))
        print(f"""
        <div style="width: 900px; margin: 0 auto; text-align: center;">
            <h2>書籍情報を更新しました</h2>
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
            <form name="form1" action="/cgi-bin/report2_edit.py" method="POST">
                <input type="hidden" name="param1" value="{param_str}">
                <button type="submit" name="id" style="width: 100px" value="{book_id}">
                    戻る
                </button>
            </form>
        </div>
        """)
    else:
        print(f'''
        <div style="width: 900px; margin: 0 auto; text-align: center;">
            <div>
            <span style="display:inline-block; width:100px;">ID :</span>
                {row["ID"]}
            </div>

            <div>
                <span style="display:inline-block; width:100px;">タイトル :</span>
                {row["TITLE"]}
            </div>

            <div>
                <span style="display:inline-block; width:100px;">著者 :</span>
                {row["AUTHOR"]}
            </div>

            <div>
                <span style="display:inline-block; width:100px;">出版社 :</span>
                {row["PUBLISHER"]}
            </div>

            <div>
                <span style="display:inline-block; width:100px;">価格 :</span>
                {row["PRICE"]}
            </div>

            <div>
                <span style="display:inline-block; width:100px;">ISBN :</span>
                {row["ISBN"]}
            </div>
            <br>
            <form name="form1" action="/cgi-bin/report2_edit.py" method="POST" style="display:inline-block;">
                <input type="hidden" name="id" value="{row['ID']}">
                <button type="submit" name="mode" style="width: 200px" value="editting">
                    編集
                </button>
            </form>

            <form name="form1" action="/cgi-bin/report2_edit.py" method="POST" style="display:inline-block;">
                <input type="hidden" name="id" value="{row['ID']}">
                <button type="submit" name="mode" style="width: 200px" value="delete">
                    削除
                </button>
            </form>

            <form name="form1" action="/cgi-bin/report2_search.py" method="POST">
                <input type="hidden" name="param1" value="{param_str}">
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