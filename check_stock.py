import os
import requests
from playwright.sync_api import sync_playwright

URL = "https://store-jp.nintendo.com/item/goods/VM_NSJ_8_BZAB4"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def check():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            # ページへアクセス
            page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            
            # メインの購入/品切れボタン要素を取得（マイニンテンドーストアのボタン判定）
            # 品切れ時は <button ... disabled>品切れ</button> のような構造になります
            sold_out_button = page.query_selector("button:has-text('品切れ')")
            
            # 「品切れ」ボタンが存在し、かつ表示されているか確認
            is_sold_out = False
            if sold_out_button and sold_out_button.is_visible():
                is_sold_out = True
            
            print(f"「品切れ」ボタン要素の検出: {is_sold_out}")
            
            # 「品切れ」ボタンが見つからなければ「カートに入れる」ボタンに変化したと判断
            if not is_sold_out:
                msg = f"【再販検知！】ピクミンの花瓶（一輪挿し 赤）の在庫が復活しました！\n{URL}"
                send_discord(msg)
                print("★ 在庫復活を検知し、Discordに通知しました！")
            else:
                print("判定結果: 現在も「品切れ」状態です。")
                
        except Exception as e:
            print(f"エラーが発生しました: {e}")
        finally:
            browser.close()

def send_discord(msg):
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": msg})

if __name__ == "__main__":
    check()
