import urllib.request
import json
import time

items_to_search = [
    "コスモクルー・ジャケット", "コスモクルー・グローブ", "コスモクルー・トラウザー", "コスモクルー・ブーツ",
    "コスモキャプテン・ハット", "コスモキャプテン_コート", "コスモキャプテン・グローブ", "コスモキャプテン・トラウザー", "コスモキャプテン・ブーツ",
    "コスモアドミラル・ヘルム", "コスモアドミラル・コート", "コスモアドミラル・グローブ", "コスモアドミラル・トラウザー", "コスモアドミラル・ブーツ",
    "スペースダルメル・ホイッスル", "量産型パワーローダー認証鍵", "レッドホイールローダー起動鍵",
    "ポートレート教材:コスモエクスプローラー1", "ポートレート教材:コスモエクスプローラー2", "ポートレート教材:コスモエクスプローラー3",
    "カード:パワーローダー", "カード:ネミングウェイ", "カード:スペースダルメル",
    "演技教本:怒りに震える", "スタイルカタログ:リーディンググラス", "スタイルカタログ:レザードレスアイパッチ1", "スタイルカタログ:レザードレスアイパッチ2",
    "オーケストリオン譜:親方シド", "オーケストリオン譜:飛空艇", "オーケストリオン譜:パッションキャロット",
    "コスモインナーウォール", "コスモフローリング", "コスモチェア", "コスモランプポスト", "コスモステーションルーフ", "コスモラウンドベンチ", "コスモガイドランプ", "コスモアンテナ", "コスモシェード"
]

results = {}

for item in items_to_search:
    try:
        url = f"https://xivapi.com/search?indexes=item&string={urllib.parse.quote(item)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data['Results']:
                # Find exact match
                match = next((r for r in data['Results'] if r['Name'] == item), data['Results'][0])
                results[item] = match['ID']
                print(f"Found: {item} -> {match['ID']}")
            else:
                print(f"Not found: {item}")
        time.sleep(0.1) # Be nice
    except Exception as e:
        print(f"Error searching {item}: {e}")

print("\n--- FINAL MAPPING ---")
print(json.dumps(results, indent=4, ensure_ascii=False))
