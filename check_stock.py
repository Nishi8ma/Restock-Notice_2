import os
import requests
from playwright.sync_api import sync_playwright

# 監視対象（ポケモンセンターオンラインの対象4商品）
ITEMS = [
    {
        "name": "炎がまたたく LEDライト ヒトモシ",
        "url": "https://www.pokemoncenter-online.com/4521329334233.html"
    },
    {
        "name": "炎がまたたく LEDライト ランプラー",
        "url": "https://www.pokemoncenter-online.com/4521329406701.html"
    },
    {
        "name": "炎がまたたく LEDライト シャンデラ",
        "url": "https://www.pokemoncenter-online.com/4521329355269.html"
    },
    {
        "name": "振り子時計 Little Daydream オタチ",
        "url": "https://www.pokemoncenter-online.com/4521329413044.html"
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
                # 画面の描画完了まで3秒待機
                page.wait_for_timeout(3000)
                
                # ポケモンセンターオンラインの売り切れ/再入荷表示テキストを取得
                sold_out_elements = page.get_by_text("売り切れ").all() + page.get_by_text("再入荷お知らせを受け取る").all()
                cart_button = page.get_by_text("カートに入れる").all()
                
                is_text_sold_out = len(sold_out_elements) > 0
                has_cart_button = len(cart_button) > 0
                
                print(f"「売り切れ/再入荷」テキスト要素数: {len(sold_out_elements)}")
                print(f"「カートに入れる」ボタン要素数: {len(cart_button)}")
                
                # 「カートに入れる」が存在し、かつ「売り切れ」要素がない場合のみ再販と判定
                if has_cart_button and not is_text_sold_out:
                    msg = f"【ポケセン再販検知！】「{name}」の在庫が復活しました！\n{url}"
                    send_discord(msg)
                    print(f"★ {name} の在庫復活を検知し、Discordに通知しました！")
                else:
                    print(f"判定結果: {name} は現在も「売り切れ」状態です。")
                
                # サーバー負荷防止のため次の商品まで1秒待機
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
