import json
import os
import urllib.request
import re
import time

INPUT_FILE = "items_to_search.txt"
OUTPUT_FILE = "universalis_ids_final.json"
TEAMCRAFT_DATA_URL = "https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/libs/data/src/lib/json/items.json"
LOCAL_DB_FILE = "teamcraft_items.json"

def download_teamcraft_data():
    """Teamcraftのアイテムデータをダウンロードしてローカルに保存する"""
    if os.path.exists(LOCAL_DB_FILE):
        print(f"Loading local database from {LOCAL_DB_FILE}...")
        with open(LOCAL_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    print("Downloading Teamcraft items database (this may take a moment)...")
    req = urllib.request.Request(TEAMCRAFT_DATA_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        
    with open(LOCAL_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    
    print("Database downloaded and saved.")
    return data

def normalize_name(name):
    """表記揺れを吸収するための正規化"""
    import jaconv
    # 全角/半角、カタカナ/ひらがなの揺れを吸収（主に全角カナへ）
    name = jaconv.h2z(name)
    # 中黒や空白を削除して比較しやすくする
    name = name.replace("・", "").replace(" ", "").replace("　", "").replace("_", "")
    # "焦がれの証書:第1種" のようなサフィックスをカットする（必要に応じて）
    name = re.sub(r':第\d+種$', '', name)
    name = re.sub(r'\sof\s証書:第\d+種$', '', name)
    return name

def _build_lookup_dict(db):
    """DBから高速な参照用辞書を作成する"""
    lookup = {}
    for item_id, names in db.items():
        if not isinstance(names, dict) or "ja" not in names:
            continue
        ja_name = names["ja"]
        if not ja_name:
            continue
        norm = normalize_name(ja_name)
        # 既に同じ名前があれば、IDの若い方（あるいは特定条件）を優先するかは任意
        # 今回は基本的に一意とみなし、上書きでOKとする
        lookup[norm] = (item_id, ja_name)
    return lookup

def find_best_match_fast(norm_query, lookup):
    """
    作成済みのルックアップ辞書から最適なアイテムをO(1)～O(N)で検索する
    1. 完全一致 (O(1))
    2. 部分一致 (辞書走査 O(N))
    """
    # 1. 完全一致
    if norm_query in lookup:
        return lookup[norm_query][0], lookup[norm_query][1]

    # 2. 完全一致がなければ、前方/部分一致を走査して最もスコアの高いものを探す
    best_id = None
    best_score = -1
    best_name = None

    for db_norm_name, (item_id, original_name) in lookup.items():
        score = 0
        if db_norm_name.startswith(norm_query):
            score = 2
        elif norm_query in db_norm_name:
            score = 1
        elif db_norm_name in norm_query:
            score = 1.5
            
        if score > best_score:
            best_score = score
            best_id = item_id
            best_name = original_name

    if best_score >= 1:
        return best_id, best_name
    return None, None

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    # 1. データベースの準備
    db = download_teamcraft_data()
    print("Building fast lookup dictionary...")
    lookup = _build_lookup_dict(db)


    # 2. 入力リストの読み込み
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        item_names = []
        for line in f:
            # "1: コスモアドミラル・コート" のようなプレフィックスを除去
            name = re.sub(r'^\d+:\s*', '', line.strip())
            if name:
                # 検索精度を上げるため、もし特殊文字等があれば正規化（今回はそのまま）
                item_names.append(name)

    print(f"Input list contains {len(item_names)} items.")

    # 3. 照合処理
    results_db = {}
    found_count = 0
    start_time = time.time()

    print("Starting local matching...")
    for i, name in enumerate(item_names):
        norm_query = normalize_name(name)
        item_id, matched_name = find_best_match_fast(norm_query, lookup)
        
        if item_id:
            # 抽出した名前ではなく元の入力名(name)をキーにするか、そのままか
            # 要件に合わせる。今回は入力名に対するIDが欲しいので name をキーとする
            results_db[name] = item_id
            found_count += 1
            if i % 100 == 0 or i == len(item_names) - 1: # ログの削減
                print(f"[{i+1}/{len(item_names)}] Found: {matched_name} (ID: {item_id})")
        else:
            if i % 100 == 0:
                print(f"[{i+1}/{len(item_names)}] Not Found: {name}")

    # 4. 結果の保存
    print(f"\nBefore save: {len(results_db)} items in memory.")
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results_db, f, indent=4, ensure_ascii=False)
        print(f"Results saved to {OUTPUT_FILE} (Size: {os.path.getsize(OUTPUT_FILE)} bytes)")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

    duration = time.time() - start_time
    print(f"\nDone! Found {found_count} / {len(item_names)} items.")
    print(f"Total time: {duration:.2f}s")

    print(f"Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

