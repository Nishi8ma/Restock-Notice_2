import os
import requests
from bs4 import BeautifulSoup

# 監視対象URL（赤ピクミンの花瓶のページURL）
URL = "https://store-jp.nintendo.com/item/goods/VM_NSJ_8_BZAB4"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def check():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(URL, headers=headers, timeout=10)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            
            # 方法1: ページ全体に「品切れ」があるか判定
            # (品切れでなくなったら「カートに入れる」等のボタンに変わるため)
            is_sold_out = "品切れ" in res.text
            
            if not is_sold_out:
                message = f"【再販検知！】ピクミンの花瓶（一輪挿し 赤）が再販された可能性があります！\n{URL}"
                send_discord(message)
                print("★ 在庫復活を検知しました！Discordに通知しました。")
            else:
                print("現在も「品切れ」状態です。")
                
        else:
            print(f"ページ取得失敗 ステータスコード: {res.status_code}")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def send_discord(msg):
    if WEBHOOK_URL:
        payload = {"content": msg}
        requests.post(WEBHOOK_URL, json=payload)
    else:
        print("WEBHOOK_URLが設定されていません。")

if __name__ == "__main__":
    check()
