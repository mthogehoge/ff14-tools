import re

with open('weather_fetcher.py', 'r', encoding='utf-8') as f:
    code = f.read()

craft_class_code = """
import math

class CraftPriceFetcher:
    def __init__(self):
        self.items = {}
        self.recipe_map = {}
        self.results = []
        self.target_ids = []
        self.raw_prices = {}
        self.prices_data = {}
        
        self.MAT_IDS = {
          "被膜形成材": "49224", "高密度軽銀鉱": "49208", "エバーキープの人工樹脂": "49225",
          "ローズガーネット原石": "49209", "マストドンの粗皮": "49226", "ロウヤシの葉": "49210",
          "トライヨラの染料": "49227", "オルコ亜麻": "49211", "ヤクテル天然水": "44034",
          "ウィンドローレル": "44041", "紫電の霊砂": "46246", "クラロウォルナット材": "44023",
          "カザナルインゴット": "44001", "ブラックスター": "44012", "ガルガンチュアレザー": "44062",
          "サンダーヤードシルク": "44033", "絶縁塗料": "49223", "エレクトロパイン原木": "49207",
          "パールグラス": "44043", "ウィンドパセリ": "44039", "ユーカリ": "44042",
          "ガーデン・ソフトウォーター": "49212", "コザマル・カモミール": "44040",
          "タングステン・エンチャントインク": "44050"
        }
        
        self.ROLE_MATS = {
            "タンク (防具5/アクセ5/武器)": {
              "被膜形成材": 16+8, "高密度軽銀鉱": 32+16, "エバーキープの人工樹脂": 10+2,  "ローズガーネット原石": 20+4,
              "マストドンの粗皮": 16, "ロウヤシの葉": 32, "トライヨラの染料": 16, "オルコ亜麻": 32,
              "ガーデン・ソフトウォーター": 15+3, "ヤクテル天然水": 5+1, "ウィンドローレル": 5+1, "紫電の霊砂": 17+3,
              "クラロウォルナット材": 1, "カザナルインゴット": 1, "ブラックスター": 5, "ガルガンチュアレザー": 1,
              "サンダーヤードシルク": 2+1
            },
            "ヒーラー (防具5/アクセ5/武器)": {
              "絶縁塗料": 2+6, "エレクトロパイン原木": 4+12, "被膜形成材": 10, "高密度軽銀鉱": 20,
              "エバーキープの人工樹脂": 10+4, "ローズガーネット原石": 20+8, "マストドンの粗皮": 16,
              "ロウヤシの葉": 32, "トライヨラの染料": 20, "オルコ亜麻": 40, "ガーデン・ソフトウォーター": 15+3,
              "ヤクテル天然水": 5+1, "パールグラス": 5+1, "紫電の霊砂": 17+3, "カザナルインゴット": 1+1,
              "ブラックスター": 5, "サンダーヤードシルク": 4
            },
            "ストライカー (防具5/アクセ5/武器)": {
              "絶縁塗料": 2, "エレクトロパイン原木": 4, "被膜形成材": 8+8, "高密度軽銀鉱": 16+16,
              "エバーキープの人工樹脂": 12+2, "ローズガーネット原石": 24+4, "マストドンの粗皮": 16,
              "ロウヤシの葉": 32, "トライヨラの染料": 20, "オルコ亜麻": 40, "ガーデン・ソフトウォーター": 15+3,
              "ヤクテル天然水": 5+1, "ウィンドパセリ": 5+1, "紫電の霊砂": 17+3, "カザナルインゴット": 1,
              "ブラックスター": 5, "サンダーヤードシルク": 4, "ガルガンチュアレザー": 1
            },
            "スレイヤー (防具5/アクセ5/武器)": {
              "被膜形成材": 16, "高密度軽銀鉱": 32, "エバーキープの人工樹脂": 10+2, "ローズガーネット原石": 20+4,
              "マストドンの粗皮": 16, "ロウヤシの葉": 32, "トライヨラの染料": 16, "オルコ亜麻": 32,
              "ガーデン・ソフトウォーター": 15+3, "ヤクテル天然水": 5+1, "ウィンドパセリ": 5+1,
              "紫電の霊砂": 17+3, "クラロウォルナット材": 1, "カザナルインゴット": 1+1, "ブラックスター": 5,
              "ガルガンチュアレザー": 1, "サンダーヤードシルク": 2, "絶縁塗料": 8, "エレクトロパイン原木": 16
            },
            "スカウト (防具5/アクセ5/武器)": {
              "絶縁塗料": 2+2, "エレクトロパイン原木": 4+4, "被膜形成材": 8+8, "高密度軽銀鉱": 16+16,
              "エバーキープの人工樹脂": 16+2, "ローズガーネット原石": 32+4, "マストドンの粗皮": 14,
              "ロウヤシの葉": 28, "トライヨラの染料": 18, "オルコ亜麻": 36, "ガーデン・ソフトウォーター": 15+3,
              "ヤクテル天然水": 5+1, "コザマル・カモミール": 5+1, "紫電の霊砂": 17+3, "カザナルインゴット": 1,
              "ブラックスター": 5+1, "ガルガンチュアレザー": 1, "サンダーヤードシルク": 3
            },
            "レンジャー (防具5/アクセ5/武器)": {
              "絶縁塗料": 2, "エレクトロパイン原木": 4, "被膜形成材": 8+6, "高密度軽銀鉱": 16+12,
              "エバーキープの人工樹脂": 16+4, "ローズガーネット原石": 32+8, "マストドンの粗皮": 14,
              "ロウヤシの葉": 28, "トライヨラの染料": 18, "オルコ亜麻": 36, "ガーデン・ソフトウォーター": 15+3,
              "ヤクテル天然水": 5+1, "コザマル・カモミール": 5+1, "紫電の霊砂": 17+3, "カザナルインゴット": 1,
              "ブラックスター": 5+1, "ガルガンチュアレザー": 1, "サンダーヤードシルク": 3
            },
            "キャスター (防具5/アクセ5/武器)": {
              "絶縁塗料": 2, "エレクトロパイン原木": 4, "被膜形成材": 10+6, "高密度軽銀鉱": 20+12,
              "エバーキープの人工樹脂": 10, "ローズガーネット原石": 20, "マストドンの粗皮": 16,
              "ロウヤシの葉": 32, "トライヨラの染料": 20+4, "オルコ亜麻": 40+8, "ガーデン・ソフトウォーター": 15+3,
              "ヤクテル天然水": 5+1, "ユーカリ": 5+1, "紫電の霊砂": 17+3, "カザナルインゴット": 1,
              "ブラックスター": 5, "サンダーヤードシルク": 4, "タングステン・エンチャントインク": 1
            }
        }
        self._load_data()

    def _load_data(self):
        try:
            with open('../universalis_tools/teamcraft_items.json', 'r', encoding='utf-8') as f:
                self.items = json.load(f)
        except Exception as e:
            print('Failed to open teamcraft_items.json', e)

        print('Loading recipes.json...')
        if os.path.exists('../recipes.json'):
            with open('../recipes.json', 'r', encoding='utf-8') as f:
                recipes = json.load(f)
        else:
            print('recipes.json not found. Fetching...')
            url = 'https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/staging/libs/data/src/lib/json/recipes.json'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            try:
                with urllib.request.urlopen(req) as response:
                    recipes = json.loads(response.read().decode())
                    with open('../recipes.json', 'w', encoding='utf-8') as f:
                        json.dump(recipes, f)
            except Exception as e:
                print('Error fetching recipes.json:', e)
                recipes = {}
                
        if isinstance(recipes, dict):
            for r_id, r in recipes.items():
                if 'result' in r:
                    self.recipe_map[r['result']] = r
        elif isinstance(recipes, list):
            for r in recipes:
                if 'result' in r:
                    self.recipe_map[r['result']] = r
                    
        for item_id, names in self.items.items():
            if 'ja' in names and 'コートリーラヴァー' in names['ja']:
                if not names['ja'].endswith('SP'):
                    self.results.append((int(item_id), names['ja']))
                    self.target_ids.append(int(item_id))

        print(f'CraftPriceFetcher initialized: {len(self.results)} items, {len(self.recipe_map)} recipes')

    def get_base_mats_and_crafts(self, item_id, amount=1):
        mats = {}
        crafts = 0
        recipe = self.recipe_map.get(item_id)
        if not recipe:
            return {item_id: amount}, 0
        
        yields = recipe.get('yields', 1)
        craft_times = math.ceil(amount / yields)
        crafts += craft_times
        
        ingredients = recipe.get('ingredients', [])
        for ing in ingredients:
            ing_id = ing['id']
            ing_amt = ing['amount'] * craft_times
            sub_mats, sub_crafts = self.get_base_mats_and_crafts(ing_id, ing_amt)
            crafts += sub_crafts
            for sub_id, sub_amt in sub_mats.items():
                mats[sub_id] = mats.get(sub_id, 0) + sub_amt
                
        return mats, crafts

craft_fetcher = CraftPriceFetcher()

def fetch_and_generate_craft_html():
    raw_prices = {}
    all_required_mats = set()
    for item_id, _ in craft_fetcher.results:
        mats, _ = craft_fetcher.get_base_mats_and_crafts(item_id)
        all_required_mats.update([str(k) for k in mats.keys()])
    all_required_mats = list(all_required_mats)

    print(f"Fetching raw material prices for {len(all_required_mats)} base materials...")
    for i in range(0, len(all_required_mats), 50):
        batch = all_required_mats[i:i+50]
        url = f'https://universalis.app/api/v2/Mana/{",".join(batch)}?listings=5&entries=0'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                if "items" in data:
                    for i_id, i_data in data["items"].items():
                        listings = i_data.get('listings', [])
                        min_p = 0
                        if listings:
                            sl = sorted(listings, key=lambda x: x.get('pricePerUnit', 0))
                            for listing in sl:
                                p = listing.get('pricePerUnit', 0)
                                if p > 1:
                                    min_p = p
                                    break
                            if min_p == 0 and sl:
                                min_p = sl[0].get('pricePerUnit', 0)
                        raw_prices[str(i_id)] = min_p
        except Exception as e:
            print(f"Error fetching raw mats: {e}")

    batch_size = 50 
    item_ids = [str(id) for id, _ in craft_fetcher.results]
    prices_data = {}

    print(f"Fetching prices for {len(item_ids)} crafted items...")
    for i in range(0, len(item_ids), batch_size):
        batch = item_ids[i:i+batch_size]
        url = f'https://universalis.app/api/v2/Mana/{",".join(batch)}?listings=5&entries=0'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                if "items" in data:
                    prices_data.update(data["items"])
        except Exception as e:
            print(f"Error fetching batch {i}: {e}")

    total_profit = 0
    total_time = 0
    total_valid_items = 0

    individual_calc = []
    for item_id, name in craft_fetcher.results:
        mats, crafts = craft_fetcher.get_base_mats_and_crafts(item_id)
        time_seconds = crafts * 90
        
        craft_cost = 0
        for m_id, m_amt in mats.items():
            craft_cost += raw_prices.get(str(m_id), 0) * m_amt
            
        price_info = prices_data.get(str(item_id), {})
        listings = price_info.get('listings', [])
        last_upload = price_info.get('lastUploadTime', 0)
        
        min_price = 0
        if listings:
            sorted_listings = sorted(listings, key=lambda x: x.get('pricePerUnit', 0))
            for listing in sorted_listings:
                price = listing.get('pricePerUnit', 0)
                if price > 1:
                    min_price = price
                    break
            if min_price == 0 and sorted_listings:
                min_price = sorted_listings[0].get('pricePerUnit', 0)
                
        profit = min_price - craft_cost if min_price > craft_cost else 0
        
        if min_price > 0 and profit > 0:
            total_profit += profit
            total_time += time_seconds
            total_valid_items += 1
            
        individual_calc.append({
            'id': item_id,
            'name': name,
            'min_price': min_price,
            'last_upload': last_upload,
            'mats': mats,
            'crafts': crafts,
            'time_seconds': time_seconds,
            'craft_cost': craft_cost,
            'profit': profit
        })

    hourly_profit = 0
    if total_time > 0:
        hourly_profit = (total_profit / total_time) * 3600

    role_costs = {}
    for role, rmats in craft_fetcher.ROLE_MATS.items():
        t_cost = 0
        for mat_name, qty in rmats.items():
            mat_id = craft_fetcher.MAT_IDS.get(mat_name)
            if mat_id and str(mat_id) in raw_prices:
                t_cost += raw_prices[str(mat_id)] * qty
        role_costs[role] = t_cost

    html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>新式装備（コートリーラヴァー）相場一覧</title>
    <link rel="stylesheet" href="/static/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .container {{ max-width: 900px; margin: 40px auto; }}
        .back-link {{ display: inline-block; margin-bottom: 20px; color: #4ed8d1; text-decoration: none; font-weight: bold; }}
        .back-link:hover {{ text-decoration: underline; }}
        
        .highlight-banner {{
            background: linear-gradient(135deg, rgba(78, 216, 209, 0.2) 0%, rgba(30, 42, 56, 0.9) 100%);
            border: 1px solid #4ed8d1;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .highlight-banner h2 {{ margin: 0; color: #e2f1f8; font-size: 1.4em; border: none; padding: 0; }}
        .hourly-value {{ font-size: 2.8em; font-weight: bold; color: #f7ce55; font-family: monospace; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }}
        .hourly-subtitle {{ color: #8da1b5; font-size: 0.9em; margin-top: 5px; }}

        .summary-card {{ background: rgba(30, 42, 56, 0.8); border: 1px solid rgba(247, 206, 85, 0.3); border-radius: 12px; padding: 20px; margin-bottom: 30px; }}
        .summary-card h3 {{ color: #f7ce55; margin-top: 0; border-bottom: 1px solid rgba(247, 206, 85, 0.3); padding-bottom: 10px; margin-bottom: 15px; }}
        .role-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }}
        .role-box {{ background: rgba(0, 0, 0, 0.2); padding: 15px; border-radius: 8px; border-left: 4px solid #4ed8d1; }}
        .role-name {{ font-size: 0.9em; color: #8da1b5; margin-bottom: 5px; }}
        .role-price {{ font-size: 1.4em; color: #e2f1f8; font-family: monospace; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; color: #e2f1f8; background: rgba(30, 42, 56, 0.6); backdrop-filter: blur(10px); border-radius: 12px; overflow: hidden; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }}
        th {{ background: rgba(78, 216, 209, 0.2); color: #4ed8d1; font-weight: bold; }}
        tr:hover {{ background: rgba(255, 255, 255, 0.05); }}
        .price {{ text-align: right; font-family: monospace; font-size: 1.1em; color: #f7ce55; }}
        .craft-price {{ text-align: right; font-family: monospace; font-size: 1.1em; color: #4ed8d1; }}
        .diff-cheaper {{ color: #51f574; font-size: 0.85em; font-weight: bold;}}
        .diff-expensive {{ color: #f55151; font-size: 0.85em; }}
        
        .expandable-row {{ cursor: pointer; transition: background 0.2s; }}
        .expandable-row:hover {{ background: rgba(255, 255, 255, 0.1) !important; }}
        .details-row {{ display: none; background: rgba(0, 0, 0, 0.3); }}
        .details-row.open {{ display: table-row; }}
        .details-content {{ padding: 15px 30px !important; }}
        .materials-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; background: rgba(30, 42, 56, 0.4); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); }}
        .materials-table th, .materials-table td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.9em; }}
        .materials-table th {{ background: rgba(78, 216, 209, 0.1); color: #4ed8d1; }}
        .mat-price {{ text-align: right; color: #f7ce55; font-family: monospace; }}
        .sub-info {{ font-size: 0.85em; color: #8da1b5; margin-top: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link"><i class="fas fa-arrow-left"></i> ダッシュボードへ戻る</a>
        
        <div class="highlight-banner">
            <h2><i class="fas fa-stopwatch"></i> 現在の新式金策 期待時給（全体平均）</h2>
            <div class="hourly-value">{int(hourly_profit):,} <span style="font-size: 0.5em; color: #e2f1f8;">gil / 1時間</span></div>
            <div class="hourly-subtitle">
                ※マクロ1周90秒として完成品・中間素材の全工程数を積算。<br>
                新式装備{len(individual_calc)}種の平均マケボ価格と原価率（素材購入時）の利益率から算出。
            </div>
        </div>
        
        <div class="summary-card">
            <h3><i class="fas fa-coins"></i> ロール別・新式一式（左5＋右5＋武器）の素材原価</h3>
            <p style="font-size: 0.85em; color: #8da1b5; margin-bottom: 15px;">末端素材（伝説素材・数理・霊砂など）を現在のマケボ最安値ですべて買い集めた場合の合計金額（Mana）です。<br>※「らうねの工房」様の素材算出結果に基づき計算しています。耐久35素材の各1工程分を含みます。</p>
            <div class="role-grid">
'''

    for role, t_cost in role_costs.items():
        html_content += f'''
                <div class="role-box">
                    <div class="role-name">{role}</div>
                    <div class="role-price">{int(t_cost):,} <span style="font-size: 0.6em; color: #8da1b5;">gil</span></div>
                </div>
        '''

    html_content += '''
            </div>
        </div>

        <div class="glass-card">
            <h2><i class="fas fa-gem"></i> コートリーラヴァー個別完成品 相場一覧 (Mana)</h2>
            <p style="color: #8da1b5; margin-bottom: 20px;">各装備のマケボ最安値と自作原価に加え、必要マクロ周回数からの予想製作時間も表示しています。</p>
            <table>
                <thead>
                    <tr>
                        <th style="width: 50px;"></th>
                        <th>アイテム名<br><span style="font-size: 0.8em; font-weight: normal; color: #8da1b5;">(クリックで詳細)</span></th>
                        <th style="text-align: right;">マケボ最安値</th>
                        <th style="text-align: right;">素材原価 / 粗利</th>
                        <th>更新日時</th>
                    </tr>
                </thead>
                <tbody>
'''

    for item in individual_calc:
        item_id = item['id']
        name = item['name']
        min_price = item['min_price']
        last_upload = item['last_upload']
        mats = item['mats']
        crafts = item['crafts']
        time_seconds = item['time_seconds']
        craft_cost = item['craft_cost']
        profit = item['profit']

        time_mins = time_seconds / 60
        
        price_str = f"{min_price:,} gil" if min_price > 0 else "出品なし"
        date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(last_upload / 1000)) if last_upload > 0 else "-"
        
        craft_price_str = f"{int(craft_cost):,} gil"
        
        diff_html = ""
        if min_price > 0 and craft_cost > 0:
            if profit > 0:
                diff_html = f'<br><span class="diff-cheaper">＋利益 {int(profit):,}g</span>'
            else:
                diff_html = f'<br><span class="diff-expensive">利益なし（赤字）</span>'
                
        html_content += f'''
                    <tr class="expandable-row" data-target="details-{item_id}">
                        <td><img src="https://universalis.app/api/v2/icon/{item_id}" alt="" style="width: 32px; height: 32px; border-radius: 4px;" onerror="this.style.display='none'"></td>
                        <td>
                            <a href="https://universalis.app/market/{item_id}" target="_blank" style="color: #e2f1f8; text-decoration: none;" onclick="event.stopPropagation();">{name}</a>
                            <div class="sub-info">製作目安: 約{time_mins:.1f}分 (計{crafts}工程)</div>
                        </td>
                        <td class="price">{price_str}</td>
                        <td class="craft-price">{craft_price_str}{diff_html}</td>
                        <td style="font-size: 0.9em; color: #8da1b5;">{date_str}</td>
                    </tr>
                    <tr id="details-{item_id}" class="details-row">
                        <td colspan="5" class="details-content">
                            <table class="materials-table">
                                <thead>
                                    <tr>
                                        <th>素材名</th>
                                        <th>必要数</th>
                                        <th style="text-align: right;">単価 (Mana最安値)</th>
                                        <th style="text-align: right;">小計</th>
                                    </tr>
                                </thead>
                                <tbody>
        '''

        sorted_mats = sorted(mats.items(), key=lambda x: raw_prices.get(str(x[0]), 0) * x[1], reverse=True)
        
        for m_id, m_amt in sorted_mats:
            mat_name = craft_fetcher.items.get(str(m_id), {}).get('ja', 'Unknown')
            mat_price = raw_prices.get(str(m_id), 0)
            sub_total = int(mat_price * m_amt)
            
            html_content += f'''
                                    <tr>
                                        <td>{mat_name}</td>
                                        <td>{m_amt:g}</td>
                                        <td class="mat-price">{mat_price:,} gil</td>
                                        <td class="mat-price">{sub_total:,} gil</td>
                                    </tr>
            '''
            
        html_content += '''
                                </tbody>
                            </table>
                        </td>
                    </tr>
        '''

    html_content += '''
                </tbody>
            </table>
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const rows = document.querySelectorAll('.expandable-row');
            rows.forEach(row => {
                row.addEventListener('click', function() {
                    const targetId = this.getAttribute('data-target');
                    const detailsRow = document.getElementById(targetId);
                    if (detailsRow.classList.contains('open')) {
                        detailsRow.classList.remove('open');
                    } else {
                        document.querySelectorAll('.details-row.open').forEach(r => r.classList.remove('open'));
                        detailsRow.classList.add('open');
                    }
                });
            });
        });
    </script>
</body>
</html>
'''
    return html_content
"""

# class WeatherRequestHandler... の前に craft_class_code を挿入する
insert_pos = code.find('class WeatherRequestHandler')
new_code = code[:insert_pos] + craft_class_code + '\n' + code[insert_pos:]

# try: の中の elf.path == '/' 系のところに '/craft' を追加する
handler_repl = """            if self.path == '/':
                # 1. コンテンツを生成 (エラーが出れば例外処理へ)
                forecasts = generate_forecast()
                html_content = generate_html(forecasts)
                body = html_content.encode('utf-8')
                
                # 2. 正常終了した場合のみヘッダーを送信
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                
            elif self.path == '/craft':
                try:
                    html_content = fetch_and_generate_craft_html()
                    body = html_content.encode('utf-8')
                    self.send_response(200)
                    self.send_header("Content-type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                except Exception as e:
                    self.send_error(500, f"Error generating craft html: {e}")"""
                    
new_code = re.sub(r'            if self\.path == \'/\':.*?(?=\s+elif self\.path == \'/static/style\.css\':)', handler_repl, new_code, flags=re.DOTALL)

with open('weather_fetcher.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
