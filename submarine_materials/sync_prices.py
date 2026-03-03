import json
import os

cache_path = r'c:\Users\81909\Desktop\ff14\cosmo_dashboard\market_cache.json'
output_path = r'c:\Users\81909\Desktop\ff14\submarine_materials\prices.js'

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
