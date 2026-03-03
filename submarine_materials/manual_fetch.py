import urllib.request
import json
import time

# 潜水艦素材（全251項目）
SUB_IDS = [2, 3, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 5057, 5058, 5059, 5060, 5061, 5064, 5065, 5066, 5067, 5068, 5069, 5073, 5074, 5075, 5079, 5092, 5093, 5094, 5095, 5099, 5106, 5111, 5113, 5114, 5115, 5116, 5118, 5119, 5120, 5121, 5143, 5149, 5163, 5190, 5226, 5232, 5261, 5262, 5263, 5287, 5314, 5339, 5346, 5366, 5371, 5373, 5378, 5379, 5384, 5388, 5390, 5395, 5436, 5485, 5491, 5501, 5505, 5506, 5507, 5512, 5518, 5522, 5523, 5525, 5526, 5528, 5530, 5532, 5553, 5558, 5728, 7017, 7018, 7019, 7022, 7023, 7588, 7589, 7590, 7596, 7597, 7598, 7601, 7606, 7607, 8029, 9359, 9360, 9369, 12220, 12221, 12223, 12224, 12231, 12232, 12518, 12519, 12520, 12521, 12522, 12523, 12524, 12525, 12526, 12528, 12530, 12531, 12532, 12533, 12534, 12535, 12536, 12537, 12538, 12539, 12541, 12551, 12563, 12565, 12569, 12571, 12578, 12579, 12580, 12581, 12582, 12583, 12602, 12604, 12605, 12606, 12609, 12629, 12631, 12632, 12634, 12635, 12636, 12882, 12912, 12913, 12932, 12937, 12943, 12944, 13750, 13758, 14146, 14147, 14148, 14149, 14150, 14151, 14935, 15649, 16908, 19910, 19925, 19930, 19938, 19947, 19950, 19957, 19962, 19967, 19968, 19973, 19993, 19999, 21792, 21793, 21794, 21795, 21796, 21797, 21798, 21799, 22526, 22527, 22528, 22529, 23903, 23904, 23905, 23906, 24344, 24345, 24346, 24347, 24348, 24349, 24350, 24351, 24352, 24353, 24354, 24355, 24356, 24357, 24358, 24359, 24360, 24361, 24362, 24363, 24364, 24365, 24366, 24367, 25008, 25009, 26508, 26509, 26510, 26511, 26512, 26513, 26514, 26515, 26516, 26517, 26518, 26519, 26520, 26521, 26522, 26523, 26524, 26525, 26526, 26527, 26529, 26530, 26531, 26532]

cache_path = r'c:\Users\81909\Desktop\ff14\cosmo_dashboard\market_cache.json'
prices_js_path = r'c:\Users\81909\Desktop\ff14\submarine_materials\prices.js'

def fetch_and_sync():
    print(f"Starting fetch for {len(SUB_IDS)} items...")
    
    # Load current cache
    cache = {}
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)

    chunk_size = 100
    for i in range(0, len(SUB_IDS), chunk_size):
        chunk = [str(id) for id in SUB_IDS[i:i+chunk_size]]
        ids_str = ",".join(chunk)
        url = f"https://universalis.app/api/v2/Japan/{ids_str}?listings=1"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                
                items = data.get('items', {})
                # If only one item, it might be a direct object instead of 'items'
                if not items and len(chunk) == 1:
                    items = {chunk[0]: data}
                
                for iid, info in items.items():
                    listings = info.get('listings', [])
                    if listings:
                        price = listings[0].get('pricePerUnit', 0)
                        cache[str(iid)] = {
                            'price': price,
                            'timestamp': time.time(),
                            'server': listings[0].get('worldName', 'Unknown')
                        }
            print(f"Fetched chunk {i//chunk_size + 1}")
            time.sleep(1) # Rate limit safety
        except Exception as e:
            print(f"Error fetching chunk {i//chunk_size + 1}: {e}")

    # Save cache
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    # Sync to prices.js
    with open(prices_js_path, 'w', encoding='utf-8') as f:
        f.write("const MARKET_PRICES = ")
        json.dump(cache, f, ensure_ascii=False)
        f.write(";")
    
    print("Done! market_cache.json and prices.js updated.")

if __name__ == "__main__":
    import os
    fetch_and_sync()
