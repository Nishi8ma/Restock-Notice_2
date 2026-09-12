import os
import requests
from playwright.sync_api import sync_playwright

ITEMS = [
    {
        "name": "一輪挿し 赤 PIKMIN",
        "url": "https://store-jp.nintendo.com/item/goods/VM_NSJ_8_BZAB4"
    },
    {
        "name": "一輪挿し 青 PIKMIN",
        "url": "https://store-jp.nintendo.com/item/goods/VM_NSJ_8_BZAB5"
    },
    {
        "name": "一輪挿し 黄 PIKMIN",
        "url": "https://store-jp.nintendo.com/item/goods/VM_NSJ_8_BZAB6"
    }
]

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
            for item in ITEMS:
                name = item["name"]
                url = item["url"]
                
                print(f"--- チェック中: {name} ---")
                
                # ネットワーク通信が落ち着くまでしっかり待機
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(2000)
                
                # 判定方法1: 画面内の「品切れ」という文字が含まれる要素を探す
                sold_out_elements = page.get_by_text("品切れ").all()
                is_text_sold_out = len(sold_out_elements) > 0
                
                # 判定方法2: 「カートに入れる」という購入可能ボタンが存在するか探す
                cart_button = page.get_by_text("カートに入れる").all()
                has_cart_button = len(cart_button) > 0
                
                print(f"「品切れ」テキスト要素数: {len(sold_out_elements)}")
                print(f"「カートに入れる」ボタン要素数: {len(cart_button)}")
                
                # 「カートに入れる」が存在し、かつ「品切れ」要素がない場合のみ再販と判定
                if has_cart_button and not is_text_sold_out:
                    msg = f"【再販検知！】「{name}」の在庫が復活しました！\n{url}"
                    send_discord(msg)
                    print(f"★ {name} の在庫復活を検知し、Discordに通知しました！")
                else:
                    print(f"判定結果: {name} は現在も「品切れ」状態です。")
                
                page.wait_for_timeout(1000)
                
        except Exception as e:
            print(f"エラーが発生しました: {e}")
        finally:
            browser.close()

def send_discord(msg):
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": msg})

if __name__ == "__main__":
    check()
