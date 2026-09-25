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
                page.wait_for_timeout(3000)
                
                # ポケセンのメインエリア内にある「売り切れ」または「再入荷お知らせ」要素を取得
                # 売り切れ時は「売り切れ」「再入荷お知らせを受け取る」等のボタンまたはテキストが表示されます
                sold_out_btn = page.query_selector("*:has-text('売り切れ')") or page.query_selector("*:has-text('再入荷お知らせ')")
                
                # 画面全体の「売り切れ/再入荷」関連要素をチェック
                sold_out_texts = page.get_by_text("売り切れ").all() + page.get_by_text("再入荷お知らせ").all()
                is_sold_out = len(sold_out_texts) > 0
                
                print(f"「売り切れ / 再入荷」判定要素数: {len(sold_out_texts)}")
                
                # 「売り切れ/再入荷」テキスト・ボタンが一切検出されない場合のみ再販と判定
                if not is_sold_out:
                    msg = f"【ポケセン再販検知！】「{name}」の在庫が復活しました！\n{url}"
                    send_discord(msg)
                    print(f"★ {name} の在庫復活を検知し、Discordに通知しました！")
                else:
                    print(f"判定結果: {name} は現在も「売り切れ」状態です。")
                
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
