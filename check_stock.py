import os
import requests
from playwright.sync_api import sync_playwright

# 監視対象（赤・青・黄のピクミン花瓶リスト）
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
                
                # ページへアクセス
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)
                
                # 「品切れ」ボタン要素を取得
                sold_out_button = page.query_selector("button:has-text('品切れ')")
                
                is_sold_out = False
                if sold_out_button and sold_out_button.is_visible():
                    is_sold_out = True
                
                print(f"「品切れ」ボタン検出: {is_sold_out}")
                
                # 「品切れ」ボタンが消えていれば通知
                if not is_sold_out:
                    msg = f"【再販検知！】「{name}」の在庫が復活しました！\n{url}"
                    send_discord(msg)
                    print(f"★ {name} の在庫復活を検知し、Discordに通知しました！")
                else:
                    print(f"判定結果: {name} は現在も「品切れ」状態です。")
                
                # サーバー負荷防止のため少し間隔を空ける
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
