import json
import os

items_path = r'c:\Users\81909\Desktop\ff14\universalis_tools\teamcraft_items.json'
recipes_path = r'c:\Users\81909\Desktop\ff14\recipes.json'
output_path = r'c:\Users\81909\Desktop\ff14\submarine_materials\data.js'

SUB_PLAN = {
    'shark': {'hull': {'normal': 21792, 'modified': 22526}, 'stern': {'normal': 21793, 'modified': 22527}, 'bow': {'normal': 21794, 'modified': 22528}, 'bridge': {'normal': 21795, 'modified': 22529}},
    'unkiu': {'hull': {'normal': 21796, 'modified': 24344}, 'stern': {'normal': 21800, 'modified': 24345}, 'bow': {'normal': 21804, 'modified': 24346}, 'bridge': {'normal': 21808, 'modified': 24347}},
    'whale': {'hull': {'normal': 21797, 'modified': 24348}, 'stern': {'normal': 21801, 'modified': 24349}, 'bow': {'normal': 21805, 'modified': 24350}, 'bridge': {'normal': 21809, 'modified': 24351}},
    'coelacanth': {'hull': {'normal': 21798, 'modified': 24352}, 'stern': {'normal': 21802, 'modified': 24353}, 'bow': {'normal': 21806, 'modified': 24354}, 'bridge': {'normal': 21810, 'modified': 24355}},
    'syldra': {'hull': {'normal': 21799, 'modified': 24356}, 'stern': {'normal': 21803, 'modified': 24357}, 'bow': {'normal': 21807, 'modified': 24358}, 'bridge': {'normal': 21811, 'modified': 24359}}
}

def extract_data():
    with open(items_path, 'r', encoding='utf-8') as f:
        items = json.load(f)
    with open(recipes_path, 'r', encoding='utf-8') as f:
        recipes = json.load(f)

    needed_ids = set()
    for class_data in SUB_PLAN.values():
        for part in class_data.values():
            needed_ids.add(part['normal'])
            needed_ids.add(part['modified'])

    current_ids = set(needed_ids)
    all_needed_recipes = []
    
    for _ in range(5):
        new_ids = set()
        for r in recipes:
            if r['result'] in current_ids:
                all_needed_recipes.append(r)
                for ing in r['ingredients']:
                    new_ids.add(ing['id'])
        if not new_ids: break
        needed_ids.update(new_ids)
        current_ids = new_ids

    final_items = {str(k): items[str(k)]['ja'] for k in needed_ids if str(k) in items}
    
    data = {
        'items': final_items,
        'recipes': all_needed_recipes,
        'submarine_parts': SUB_PLAN
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("const SUBMARINE_DATA = ")
        json.dump(data, f, ensure_ascii=False)
        f.write(";")
    
    print(f"Extracted {len(final_items)} items and {len(all_needed_recipes)} recipes.")

if __name__ == "__main__":
    extract_data()
