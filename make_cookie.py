from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 画面表示あり
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.streetfighter.com/6/buckler/ja-jp/auth/loginep?redirect_url=/")

    print("ブラウザでログインしてください。ログイン完了後、Enterキーを押してください。")
    input()

    # ログイン状態を保存
    context.storage_state(path="auth.json")
    print("auth.json を保存しました。")

    browser.close()