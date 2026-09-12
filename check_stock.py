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
                
                # ページへアクセス（基本DOM読み込みまで）
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # 「品切れ」または「カート」ボタンが表示されるまで最大10秒待つ
                try:
                    page.wait_for_selector("text=品切れ, text=カートに入れる", timeout=10000)
                except Exception:
                    print("ボタンの読み込みタイムアウト（描画待ち継続）")
                
                page.wait_for_timeout(2000)
                
                # 画面内のテキスト要素をチェック
                sold_out_elements = page.get_by_text("品切れ").all()
                cart_button = page.get_by_text("カートに入れる").all()
                
                is_text_sold_out = len(sold_out_elements) > 0
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
