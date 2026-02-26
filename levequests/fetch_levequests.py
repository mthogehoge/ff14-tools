import urllib.request
import json
import time

def get_expansion(level):
    if level <= 50:
        return 'A Realm Reborn (新生)'
    elif level <= 60:
        return 'Heavensward (蒼天)'
    elif level <= 70:
        return 'Stormblood (紅蓮)'
    elif level <= 80:
        return 'Shadowbringers (漆黒)'
    elif level <= 90:
        return 'Endwalker (暁月)'
    else:
        return 'Dawntrail (黄金)'

def fetch_all_crafting_levequests():
    base_url = "https://xivapi.com/Leve"
    columns = "ID,Name_ja,ClassJobLevel,ClassJobCategory.Name_ja,CraftLeve.Item0.Name_ja,CraftLeve.Item0TargetID,CraftLeve.ItemCount0"
    limit = 100
    page = 1
    total_pages = 1
    
    # Target crafting class job categories (Japanese names from XIVAPI)
    crafting_classes = [
        "木工師", "鍛冶師", "甲冑師", "彫金師", 
        "革細工師", "裁縫師", "錬金術師", "調理師"
    ]
    
    levequests_data = {
        'A Realm Reborn (新生)': {job: [] for job in crafting_classes},
        'Heavensward (蒼天)': {job: [] for job in crafting_classes},
        'Stormblood (紅蓮)': {job: [] for job in crafting_classes},
        'Shadowbringers (漆黒)': {job: [] for job in crafting_classes},
        'Endwalker (暁月)': {job: [] for job in crafting_classes},
        'Dawntrail (黄金)': {job: [] for job in crafting_classes},
    }

    print("Fetching leveled data from XIVAPI...")

    while page <= total_pages:
        url = f"{base_url}?columns={columns}&limit={limit}&page={page}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        try:
            response = urllib.request.urlopen(req)
            data = json.loads(response.read())
            
            if page == 1:
                total_pages = data['Pagination']['PageTotal']
                print(f"Total pages to fetch: {total_pages}")
                
            results = data['Results']
            for result in results:
                # Check if it's a crafting levequest by category and has required items
                if not result.get('ClassJobCategory') or not result.get('CraftLeve'):
                    continue
                    
                job_category = result['ClassJobCategory'].get('Name_ja')
                if job_category not in crafting_classes:
                    continue
                    
                item_id = result['CraftLeve'].get('Item0TargetID')
                item_name = result['CraftLeve'].get('Item0', {}).get('Name_ja') if result['CraftLeve'].get('Item0') else None
                item_count = result['CraftLeve'].get('ItemCount0')
                leve_name = result.get('Name_ja')
                level = result.get('ClassJobLevel', 0)
                
                if not item_id or not item_name:
                    continue
                    
                expansion = get_expansion(level)
                
                leve_info = {
                    'leve_id': result['ID'],
                    'leve_name': leve_name,
                    'level': level,
                    'item_id': item_id,
                    'item_name': item_name,
                    'item_count': item_count
                }
                
                levequests_data[expansion][job_category].append(leve_info)
                
            print(f"Processed page {page}/{total_pages}")
            page += 1
            time.sleep(0.1) # Be nice to the API
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    # Sort the items by level within each job/expansion
    for exp in levequests_data:
        for job in levequests_data[exp]:
            levequests_data[exp][job] = sorted(levequests_data[exp][job], key=lambda x: x['level'])

    output_file = 'levequests.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(levequests_data, f, ensure_ascii=False, indent=2)
        
    print(f"\nSuccessfully saved {output_file}")

if __name__ == "__main__":
    fetch_all_crafting_levequests()
