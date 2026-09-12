import os
import requests
from playwright.sync_api import sync_playwright

URL = "https://store-jp.nintendo.com/item/goods/VM_NSJ_8_BZAB4"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def check():
    with sync_playwright() as p:
        # ブラウザ（Chromium）を起動
        browser = p.chromium.launch(headless=True)
        # 本物のPCブラウザに見せかける設定
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            # ページへアクセスしてJavaScriptの実行を待つ
            page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            # ページの読み込み完了まで数秒待機
            page.wait_for_timeout(3000)
            
            # 画面全体のテキストを取得
            content_text = page.content()
            
            print(f"取得データサイズ（JavaScript描画後）: {len(content_text)} バイト")
            
            has_sold_out = "品切れ" in content_text
            has_cart = "カートに入れる" in content_text
            
            print(f"「品切れ」テキスト検知: {has_sold_out}")
            print(f"「カートに入れる」テキスト検知: {has_cart}")
            
            # 「カートに入れる」が存在し、「品切れ」がない場合のみ再販と判定
            if has_cart and not has_sold_out:
                msg = f"【再販検知！】ピクミンの花瓶（一輪挿し 赤）の在庫が復活しました！\n{URL}"
                send_discord(msg)
                print("★ 在庫復活を検知し、Discordに通知しました。")
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
