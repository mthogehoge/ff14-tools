import json
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cache_path = os.path.join(base_dir, 'cosmo_dashboard', 'market_cache.json')
output_path = os.path.join(base_dir, 'submarine_materials', 'prices.js')

def sync():
    if not os.path.exists(cache_path):
        print("Cache not found.")
        return

    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("const MARKET_PRICES = ")
        json.dump(cache, f, ensure_ascii=False)
        f.write(";")
    
    print(f"Synced {len(cache)} items to prices.js.")

if __name__ == "__main__":
    sync()
