import urllib.request
import urllib.parse
import json

q = urllib.parse.quote('コートリーラヴァー')
url = f'https://xivapi.com/search?indexes=Recipe&string={q}&columns=ID,ItemResult.Name,ItemIngredient0.Name,AmountIngredient0,ItemIngredient1.Name,AmountIngredient1,ItemIngredient2.Name,AmountIngredient2,ItemIngredient3.Name,AmountIngredient3,ItemIngredient4.Name,AmountIngredient4,ItemIngredient5.Name,AmountIngredient5'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        if 'Results' in data and data['Results']:
            print(f"Found {len(data['Results'])} recipes. Example:")
            r = data['Results'][0]
            print(r['ItemResult']['Name'])
            for i in range(6):
                ing = r.get(f'ItemIngredient{i}')
                amt = r.get(f'AmountIngredient{i}')
                if ing and amt:
                    print(f"  - {ing['Name']} x{amt}")
        else:
            print('No results found from XIVAPI.')
except Exception as e:
    print('Failed to download recipes:', e)
