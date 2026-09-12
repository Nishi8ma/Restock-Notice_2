import os
import requests
from bs4 import BeautifulSoup

URL = "https://store-jp.nintendo.com/item/goods/VM_NSJ_8_BZAB4"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def check():
    # マイニンテンドーストアに拒否されにくい一般的なブラウザのヘッダー情報
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    }
    
    try:
        res = requests.get(URL, headers=headers, timeout=15)
        
        if res.status_code == 200:
            html_text = res.text
            
            # ログ確認用：取得したHTMLの長さを出力（極端に短い場合はアクセス拒否されている可能性あり）
            print(f"取得データサイズ: {len(html_text)} バイト")
            
            # 判定条件1: 「品切れ」という文字が含まれているか
            # 判定条件2: 「カートに入れる」という購入ボタンが存在するか
            has_sold_out_text = "品切れ" in html_text
            has_cart_button = "カートに入れる" in html_text
            
            # ログ出力（Actionsのログで確認可能）
            print(f"「品切れ」表記の検知: {has_sold_out_text}")
            print(f"「カートに入れる」表記の検知: {has_cart_button}")
            
            # 安全な判定：明確に「カートに入れる」が存在し、かつ「品切れ」がない場合のみ通知
            if has_cart_button and not has_sold_out_text:
                message = f"【再販検知！】ピクミンの花瓶（一輪挿し 赤）の在庫が復活した可能性があります！\n{URL}"
                send_discord(message)
                print("★ 在庫復活を検知し、Discordへ通知しました。")
            else:
                print("判定結果: 現在も品切れ中（または準備中）です。")
                
        else:
            print(f"アクセス失敗 ステータスコード: {res.status_code}")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def send_discord(msg):
    if WEBHOOK_URL:
        payload = {"content": msg}
        requests.post(WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    check()
