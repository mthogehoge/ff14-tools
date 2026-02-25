import urllib.request
import json
import os

print('Loading teamcraft_items.json...')
with open('universalis_tools/teamcraft_items.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

target_ids = []
for k, v in items.items():
    if 'ja' in v and 'コートリーラヴァー' in v['ja'] and not v['ja'].endswith('SP'):
        target_ids.append(int(k))

print('Loading recipes.json...')
if os.path.exists('recipes.json'):
    with open('recipes.json', 'r', encoding='utf-8') as f:
        recipes = json.load(f)
else:
    url = 'https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/staging/libs/data/src/lib/json/recipes.json'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        recipes = json.loads(response.read().decode())
        with open('recipes.json', 'w', encoding='utf-8') as f:
            json.dump(recipes, f)

recipe_map = {}
# recipes is likely a dict: { recipeId: { ... } } or a list.
if isinstance(recipes, dict):
    for r_id, r in recipes.items():
        if 'result' in r:
            recipe_map[r['result']] = r
elif isinstance(recipes, list):
    for r in recipes:
        if 'result' in r:
            recipe_map[r['result']] = r

print(f"Loaded {len(recipe_map)} recipes.")

def get_base_mats(item_id, amount=1):
    mats = {}
    recipe = recipe_map.get(item_id)
    if not recipe:
        return {item_id: amount}
    
    yields = recipe.get('yields', 1)
    ingredients = recipe.get('ingredients', [])
    
    for ing in ingredients:
        ing_id = ing['id']
        ing_amt = ing['amount'] * amount / yields
        
        # recurse
        sub_mats = get_base_mats(ing_id, ing_amt)
        for sub_id, sub_amt in sub_mats.items():
            mats[sub_id] = mats.get(sub_id, 0) + sub_amt
            
    return mats

for target in target_ids[:3]:
    print(f"\nSample item: {items[str(target)]['ja']}")
    mats = get_base_mats(target)
    for m_id, m_amt in mats.items():
        mat_name = items.get(str(m_id), {}).get('ja', m_id)
        if mat_name == "ウォータークリスタル" or "クリスタル" in mat_name or "クラスター" in mat_name:
            continue
        print(f"  {mat_name}: {m_amt}")
