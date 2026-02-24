import os
import time
import math
import json
import urllib.request
from datetime import datetime
import http.server
import socketserver
from EorzeaEnv import EorzeaWeather, EorzeaLang

ZONES = [
    {
        "en_name": "The Tempest",
        "title": "テンペスト（オイジュス）",
        "condition_disp": "快晴 / 曇り",
        "match": ["快晴", "曇り"]
    },
    {
        "en_name": "Eastern Thanalan",
        "title": "東ザナラーン（パエンナ）",
        "condition_disp": "雨 / 曇り",
        "match": ["雨", "曇り"]
    },
    {
        "en_name": "Ultima Thule",
        "title": "ウルティマ・トゥーレ（焦がれの入り江）",
        "condition_disp": "雷霊風 / 月砂塵",
        "match": ["雷霊風", "月砂塵"]
    }
]

# 各エリアのミッションスケジュール（クラフター/ギャザラーEX+、Aランクなど）
MISSION_DATA = [
    {
        "area": "テンペスト（オイジュス）",
        "schedule": [
            {"time": "ET 00:00～03:59", "mission": "EX+: 甲冑師"},
            {"time": "ET 04:00～07:59", "mission": "EX+: 彫金師"},
            {"time": "ET 04:00～07:59", "mission": "EX+: 漁師"},
            {"time": "ET 04:00～07:59", "mission": "Aランク: 採掘師"},
            {"time": "ET 08:00～11:59", "mission": "EX+: 革細工師"},
            {"time": "ET 08:00～11:59", "mission": "EX+: 採掘師"},
            {"time": "ET 08:00～11:59", "mission": "Aランク: 鍛冶師"},
            {"time": "ET 12:00～15:59", "mission": "EX+: 裁縫師"},
            {"time": "ET 12:00～15:59", "mission": "EX+: 園芸師"},
            {"time": "ET 16:00～19:59", "mission": "EX+: 錬金術師"},
            {"time": "ET 20:00～23:59", "mission": "EX+: 調理師"},
            {"time": "ET 20:00～23:59", "mission": "EX+: 園芸師"},
            {"time": "ET 20:00～23:59", "mission": "Aランク: 錬金術師"},
        ]
    },
    {
        "area": "東ザナラーン（パエンナ）",
        "schedule": [
            {"time": "ET 00:00～01:59", "mission": "A1: 木工師"},
            {"time": "ET 00:00～01:59", "mission": "A1: 錬金術師"},
            {"time": "ET 00:00～03:59", "mission": "EX+: 甲冑師"},
            {"time": "ET 02:00～03:59", "mission": "A1: 採掘師"},
            {"time": "ET 04:00～05:59", "mission": "A1: 鍛冶師"},
            {"time": "ET 04:00～05:59", "mission": "A1: 調理師"},
            {"time": "ET 04:00～07:59", "mission": "EX+: 彫金師"},
            {"time": "ET 04:00～07:59", "mission": "EX+: 漁師"},
            {"time": "ET 08:00～09:59", "mission": "A1: 甲冑師"},
            {"time": "ET 08:00～09:59", "mission": "A1: 漁師"},
            {"time": "ET 08:00～11:59", "mission": "EX+: 革細工師"},
            {"time": "ET 10:00～11:59", "mission": "A1: 園芸師"},
            {"time": "ET 12:00～13:59", "mission": "A1: 彫金師"},
            {"time": "ET 12:00～15:59", "mission": "EX+: 裁縫師"},
            {"time": "ET 12:00～15:59", "mission": "EX+: 採掘師"},
            {"time": "ET 16:00～17:59", "mission": "A1: 革細工師"},
            {"time": "ET 16:00～19:59", "mission": "EX+: 木工師"},
            {"time": "ET 16:00～19:59", "mission": "EX+: 錬金術師"},
            {"time": "ET 20:00～21:59", "mission": "A1: 裁縫師"},
            {"time": "ET 20:00～23:59", "mission": "EX+: 鍛冶師"},
            {"time": "ET 20:00～23:59", "mission": "EX+: 調理師"},
            {"time": "ET 20:00～23:59", "mission": "EX+: 園芸師"},
        ]
    },
    {
        "area": "ウルティマ・トゥーレ（焦がれの入り江）",
        "schedule": [
            {"time": "ET 00:00～01:59", "mission": "A1: 木工師"},
            {"time": "ET 00:00～01:59", "mission": "A1: 錬金術師"},
            {"time": "ET 00:00～01:59", "mission": "A3: 彫金師"},
            {"time": "ET 00:00～03:59", "mission": "EX+: 木工師"},
            {"time": "ET 00:00～03:59", "mission": "EX+: 漁師"},
            {"time": "ET 02:00～03:59", "mission": "A1: 採掘師"},
            {"time": "ET 04:00～05:59", "mission": "A1: 鍛冶師"},
            {"time": "ET 04:00～05:59", "mission": "A1: 調理師"},
            {"time": "ET 04:00～05:59", "mission": "A3: 革細工師"},
            {"time": "ET 04:00～07:59", "mission": "EX+: 鍛冶師"},
            {"time": "ET 04:00～07:59", "mission": "Aランク: 裁縫師"},
            {"time": "ET 06:00～07:59", "mission": "A1: 漁師"},
            {"time": "ET 08:00～09:59", "mission": "A1: 甲冑師"},
            {"time": "ET 08:00～09:59", "mission": "A3: 裁縫師"},
            {"time": "ET 08:00～11:59", "mission": "EX+: 甲冑師"},
            {"time": "ET 08:00～11:59", "mission": "EX+: 採掘師"},
            {"time": "ET 10:00～11:59", "mission": "A1: 園芸師"},
            {"time": "ET 12:00～13:59", "mission": "A1: 彫金師"},
            {"time": "ET 12:00～13:59", "mission": "A3: 木工師"},
            {"time": "ET 12:00～13:59", "mission": "A3: 錬金術師"},
            {"time": "ET 12:00～15:59", "mission": "EX+: 彫金師"},
            {"time": "ET 12:00～15:59", "mission": "Aランク: 甲冑師"},
            {"time": "ET 14:00～15:59", "mission": "A3: 採掘師"},
            {"time": "ET 16:00～17:59", "mission": "A1: 革細工師"},
            {"time": "ET 16:00～17:59", "mission": "A3: 鍛冶師"},
            {"time": "ET 16:00～17:59", "mission": "A3: 調理師"},
            {"time": "ET 16:00～19:59", "mission": "EX+: 革細工師"},
            {"time": "ET 16:00～19:59", "mission": "EX+: 園芸師"},
            {"time": "ET 20:00～21:59", "mission": "A1: 裁縫師"},
            {"time": "ET 20:00～21:59", "mission": "A3: 甲冑師"},
            {"time": "ET 20:00～23:59", "mission": "EX+: 裁縫師"},
            {"time": "ET 20:00～23:59", "mission": "Aランク: 漁師"},
            {"time": "ET 22:00～23:59", "mission": "A3: 園芸師"},
        ]
    }
]

# 各ランクごとの獲得クレジット量データ（CSVから抽出）
REWARD_DATA = [
    {
        "area": "テンペスト（オイジュス）",
        "rewards": [
            {"rank": "EX+", "cosmo": "49～65", "area": "33～43"},
            {"rank": "EX", "cosmo": "22", "area": "13"},
            {"rank": "A", "cosmo": "9～11", "area": "7～9"},
            {"rank": "B", "cosmo": "6～8", "area": "8～11"},
            {"rank": "C", "cosmo": "2", "area": "4"},
            {"rank": "D", "cosmo": "1", "area": "3～4"}
        ]
    },
    {
        "area": "東ザナラーン（パエンナ）",
        "rewards": [
            {"rank": "EX+", "cosmo": "53～98", "area": "36～65"},
            {"rank": "EX", "cosmo": "14～40", "area": "9～24"},
            {"rank": "A", "cosmo": "11～24", "area": "9～20"},
            {"rank": "B", "cosmo": "4～6", "area": "6～8"},
            {"rank": "C", "cosmo": "2～3", "area": "3～6"},
            {"rank": "D", "cosmo": "1", "area": "3～4"}
        ]
    }
]

# コスモクレジット交換アイテム一覧データ (ID付き)
COSMO_CREDIT_DATA = [
    {
        "category": "装備品",
        "items": [
            {"name": "コスモクルー・ジャケット", "price": "8,400", "id": 47929},
            {"name": "コスモクルー・グローブ", "price": "4,800", "id": 47930},
            {"name": "コスモクルー・トラウザー", "price": "7,200", "id": 47931},
            {"name": "コスモクルー・ブーツ", "price": "4,800", "id": 47932},
            {"name": "コスモキャプテン・ハット", "price": "4,800", "id": 47279},
            {"name": "コスモキャプテン・コート", "price": "8,400", "id": 47280},
            {"name": "コスモキャプテン・グローブ", "price": "4,800", "id": 47281},
            {"name": "コスモキャプテン・トラウザー", "price": "7,200", "id": 47282},
            {"name": "コスモキャプテン・ブーツ", "price": "4,800", "id": 47283},
            {"name": "コスモアドミラル・ヘルム", "price": "4,800", "id": 50303},
            {"name": "コスモアドミラル・コート", "price": "8,400", "id": 50304},
            {"name": "コスモアドミラル・グローブ", "price": "4,800", "id": 50305},
            {"name": "コスモアドミラル・トラウザー", "price": "7,200", "id": 50306},
            {"name": "コスモアドミラル・ブーツ", "price": "4,800", "id": 50307}
        ]
    },
    {
        "category": "マウント・譜面・その他",
        "items": [
            {"name": "スペースダルメル・ホイッスル", "price": "29,000", "id": 46825},
            {"name": "量産型パワーローダー認証鍵", "price": "20,000", "id": 50445},
            {"name": "レッドホイールローダー起動鍵", "price": "20,000", "id": 50446},
            {"name": "ポートレート教材:コスモエクスプローラー1", "price": "6,000"},
            {"name": "ポートレート教材:コスモエクスプローラー2", "price": "6,000"},
            {"name": "ポートレート教材:コスモエクスプローラー3", "price": "6,000"},
            {"name": "カード:パワーローダー", "price": "4,000"},
            {"name": "カード:ネミングウェイ", "price": "6,000"},
            {"name": "カード:スペースダルメル", "price": "4,000"},
            {"name": "演技教本:怒りに震える", "price": "9,600", "id": 47985},
            {"name": "スタイルカタログ:リーディンググラス", "price": "6,000", "id": 48153},
            {"name": "スタイルカタログ:レザードレスアイパッチ1", "price": "3,000", "id": 46838},
            {"name": "スタイルカタログ:レザードレスアイパッチ2", "price": "3,000", "id": 46839},
            {"name": "オーケストリオン譜:親方シド", "price": "6,000", "id": 48211},
            {"name": "オーケストリオン譜:飛空艇", "price": "6,000", "id": 48213},
            {"name": "オーケストリオン譜:パッションキャロット", "price": "6,000", "id": 46156}
        ]
    },
    {
        "category": "ハウジング",
        "items": [
            {"name": "コスモインナーウォール", "price": "4,000", "id": 49836},
            {"name": "コスモフローリング", "price": "4,000", "id": 49837},
            {"name": "コスモチェア", "price": "3,000", "id": 48732},
            {"name": "コスモランプポスト", "price": "3,000", "id": 48735},
            {"name": "コスモステーションルーフ", "price": "3,000", "id": 46176},
            {"name": "コスモラウンドベンチ", "price": "3,000", "id": 46177},
            {"name": "コスモガイドランプ", "price": "3,000", "id": 49870},
            {"name": "コスモアンテナ", "price": "3,000", "id": 49871},
            {"name": "コスモシェード", "price": "3,000", "id": 49872}
        ]
    },
    {
        "category": "消耗品",
        "items": [
            {"name": "ハイコーディアル", "price": "40"},
            {"name": "ケソ・フレスコ", "price": "30"},
            {"name": "ウールバックのロース肉", "price": "30"},
            {"name": "キャッサバ", "price": "30"},
            {"name": "最高級マテ茶葉", "price": "30"},
            {"name": "アヒ・アマリージョ", "price": "30"},
            {"name": "石匠の研磨剤", "price": "1,000", "id": 46252},
            {"name": "黄金の霊砂", "price": "200"},
            {"name": "幻岩の霊砂", "price": "400"},
            {"name": "幻葉の霊砂", "price": "400"},
            {"name": "幻海の霊砂", "price": "400"},
            {"name": "紫電の霊砂", "price": "600", "id": 46246},
            {"name": "高濃縮錬金薬", "price": "250", "id": 44848},
            {"name": "クラフターの製図用紙", "price": "30"},
            {"name": "転送網利用券:コスモエクスプローラー", "price": "60"},
            {"name": "アサリのむき身", "price": "10", "id": 43856},
            {"name": "ゴーストニッパー", "price": "10", "id": 43859},
            {"name": "紅サシ", "price": "10", "id": 43858},
            {"name": "トンボ", "price": "10", "id": 43857},
            {"name": "ホワイトワーム", "price": "10", "id": 43854},
            {"name": "ポッパールアー", "price": "100", "id": 43855}
        ]
    },
    {
        "category": "カララント",
        "items": [
            {"name": "カララント:ルビーレッド", "price": "600", "id": 30116},
            {"name": "カララント:チェリーピンク", "price": "600", "id": 30117},
            {"name": "カララント:カーマインレッド", "price": "600", "id": 48227},
            {"name": "カララント:ネオンピンク", "price": "600", "id": 48163},
            {"name": "カララント:ブライトオレンジ", "price": "600", "id": 48164},
            {"name": "カララント:カナリーイエロー", "price": "600", "id": 30118},
            {"name": "カララント:バニライエロー", "price": "600", "id": 30119},
            {"name": "カララント:ネオンイエロー", "price": "600", "id": 48166},
            {"name": "カララント:ネオングリーン", "price": "600", "id": 48165},
            {"name": "カララント:ドラグーンブルー", "price": "600", "id": 30120},
            {"name": "カララント:ターコイズブルー", "price": "600", "id": 30121},
            {"name": "カララント:アズールブルー", "price": "600", "id": 48168},
            {"name": "カララント:バイオレットパープル", "price": "600", "id": 48167},
            {"name": "カララント:ガンメタル", "price": "1,500", "id": 30122},
            {"name": "カララント:パールホワイト", "price": "1,500", "id": 30123},
            {"name": "カララント:シャインブラス", "price": "1,500", "id": 30124}
        ]
    },
    {
        "category": "マテリア",
        "items": [
            {"name": "達識のハイオメガマテリジャ", "price": "450", "id": 41762},
            {"name": "達識のハイアルテマテリジャ", "price": "900", "id": 41775},
            {"name": "博識のハイオメガマテリジャ", "price": "450", "id": 41763},
            {"name": "博識のハイアルテマテリジャ", "price": "900", "id": 41776},
            {"name": "器識のハイオメガマテリジャ", "price": "450", "id": 41764},
            {"name": "器識のハイアルテマテリジャ", "price": "900", "id": 41777},
            {"name": "名匠のハイオメガマテリジャ", "price": "450", "id": 41765},
            {"name": "名匠のハイアルテマテリジャ", "price": "900", "id": 41778},
            {"name": "魔匠のハイオメガマテリジャ", "price": "450", "id": 41766},
            {"name": "魔匠のハイアルテマテリジャ", "price": "900", "id": 41779},
            {"name": "巨匠のハイオメガマテリジャ", "price": "450", "id": 41767},
            {"name": "巨匠のハイアルテマテリジャ", "price": "900", "id": 41780}
        ]
    }
]

# レア/高額アイテム一覧データ
RARE_ITEMS_DATA = [
    {"name": "惑星パエンナ探索計画の証書", "id": 47343},
    {"name": "惑星オイジュス探索計画の証書", "id": 50829},
    {"name": "オイジュス・エネルギーパック", "id": 50414},
    {"name": "コスモ・アームドウェポン認証鍵", "id": 50442},
    {"name": "コスモボード", "id": 47336},
    {"name": "演技教本:地団駄を踏む", "id": 50334},
    {"name": "コスモフェイス認証鍵", "id": 50435}
]

# キャッシュ用グローバル変数
MARKET_PRICE_CACHE = {}
LAST_API_CALL = 0
CACHE_DURATION = 300 # 5分キャッシュ

def fetch_market_prices():
    global MARKET_PRICE_CACHE, LAST_API_CALL
    
    current_time = time.time()
    if current_time - LAST_API_CALL < CACHE_DURATION and MARKET_PRICE_CACHE:
        return MARKET_PRICE_CACHE
    
    item_ids = []
    for cat in COSMO_CREDIT_DATA:
        for item in cat['items']:
            if 'id' in item:
                item_ids.append(str(item['id']))
    
    for item in RARE_ITEMS_DATA:
        item_ids.append(str(item['id']))
    
    if not item_ids:
        return {}
        
    try:
        # Universalis API (Japan Region) - 最大100件まで一括取得可能
        item_ids_str = ",".join(item_ids[:100])
        # entries=1を指定することで負荷を抑えつつregularSaleVelocityを取得可能にする
        url = f"https://universalis.app/api/v2/Japan/{item_ids_str}?listings=0&entries=1"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'FF14_Dashboard/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            new_cache = {}
            # 複数アイテムの場合は'items'キーに含まれる
            items_data = data.get('items', {})
            if not items_data and 'minPrice' in data: # 単一アイテムの場合
                items_data = {str(data['itemID']): data}
                
            for iid, info in items_data.items():
                min_price = info.get('minPrice', 0)
                try:
                    velocity = float(info.get('regularSaleVelocity') or 0.0)
                except:
                    velocity = 0.0
                price_str = f"{min_price:,}" if min_price > 0 else "---"
                new_cache[int(iid)] = {'price': price_str, 'velocity': velocity}
            
            MARKET_PRICE_CACHE = new_cache
            LAST_API_CALL = current_time
            print(f"Market prices updated from Universalis at {datetime.now()}")
            return MARKET_PRICE_CACHE
    except Exception as e:
        print(f"Error fetching market prices: {e}")
        return MARKET_PRICE_CACHE

WEATHER_PERIOD = 1400  # 1400 LT seconds = 8 ET hours
NUM_PERIODS = 17       # 17 periods * 23.3 mins = ~6.6 hours (covers 6 hours)
PORT = 8000

def generate_forecast():
    current_lt = time.time()
    current_period_start = math.floor(current_lt / WEATHER_PERIOD) * WEATHER_PERIOD

    forecast_data = {z["en_name"]: [] for z in ZONES}

    for i in range(NUM_PERIODS):
        period_lt = current_period_start + i * WEATHER_PERIOD
        et_hour = int((period_lt / WEATHER_PERIOD * 8) % 24)
        et_str = f"ET {et_hour:02d}:00"
        lt_dt = datetime.fromtimestamp(period_lt)
        lt_str = f"(LT {lt_dt.strftime('%H:%M')})"
        
        for z in ZONES:
            w = EorzeaWeather.forecast(z["en_name"], [period_lt], lang=EorzeaLang.JA)[0]
            forecast_data[z["en_name"]].append({
                "time_text": f"{et_str} {lt_str}",
                "weather": w
            })
        
    return forecast_data

def generate_html(forecast_data):
    # テンプレートファイルを読み込む
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        html_template = f.read()
        
    weather_html = ""
    for z in ZONES:
        matches = forecast_data[z["en_name"]]
        
        weather_html += f"""
            <div class="grid-item">
                <h3 class="zone-title">{z['title']}</h3>
                <div class="condition-box">
                    <span class="icon">⚡</span> 天候EX+発生条件: <span class="white-text" style="margin-left:4px;">{z['condition_disp']}</span>
                </div>
                <div class="result-list">
"""
        if len(matches) == 0:
            weather_html += "今後6時間、該当天候なし"
        else:
            for m in matches:
                weather_html += f"""                    <div class="result-item"><span class="result-time">{m['time_text']}</span> <span class="weather-badge">{m['weather']}</span></div>\n"""
                
        weather_html += """                </div>
            </div>
"""

    # --- ミッションスケジュールエリアの生成 ---
    # 現在のET（Hour）を算出
    now_et_sec = time.time() * 144 / 7
    now_et_hour = (now_et_sec / 3600) % 24
    
    mission_html = ""
    for mdata in MISSION_DATA:
        mission_html += f"""                <div class="mission-column">
                    <div class="mission-column-title">{mdata['area']}</div>
"""
        for i, row in enumerate(mdata["schedule"]):
            # スケジュールの時間枠判定（"ET 00:00～01:59" のフォーマットから時間を取得）
            time_str = row['time'].replace('ET ', '')
            time_parts = time_str.split('～')
            
            if len(time_parts) == 2:
                start_h = int(time_parts[0].split(':')[0])
                end_str = time_parts[1].split(':')[0]
                # 23:59 のような表記の場合は時間部分に1を足して考える（あるいは等号で判定する）
                end_h = int(end_str)
                if time_parts[1].endswith('59'):
                    end_h += 1
                
                # スケジュールが日をまたぐ場合（ET 20:00～24:00など）の対処
                if start_h < end_h:
                    is_active = (start_h <= now_et_hour < end_h)
                else:
                    is_active = (now_et_hour >= start_h or now_et_hour < end_h)
            else:
                is_active = False
            
            highlight_class = " mission-highlight" if is_active else ""
            now_badge = " <span style='color:#f7ce55; font-size:10px;'>(NOW)</span>" if is_active else ""
            
            mission_html += f"""                    <div class="mission-item{highlight_class}">
                        <span class="mission-time">{row['time']}{now_badge}</span>
                        <span class="mission-name">{row['mission']}</span>
                    </div>
"""
        mission_html += """                </div>
"""

    html_template = html_template.replace("<!-- WEATHER_PLACEHOLDER -->", weather_html)
    html_template = html_template.replace("<!-- MISSION_PLACEHOLDER -->", mission_html)
    
    # --- クレジット獲得量の生成 ---
    reward_html = ""
    for rdata in REWARD_DATA:
        reward_html += f"""
            <div class="reward-column">
                <div class="reward-column-title">{rdata['area']}</div>
                <table class="reward-table">
                    <tr><th>ランク</th><th>コスモ</th><th>エリア</th></tr>
        """
        for r in rdata['rewards']:
            reward_html += f"""
                    <tr>
                        <td class="reward-rank">{r['rank']}</td>
                        <td class="reward-val">{r['cosmo']}</td>
                        <td class="reward-val">{r['area']}</td>
                    </tr>
            """
        reward_html += "                </table>\n            </div>"
    
    html_template = html_template.replace("<!-- CREDIT_REWARD_PLACEHOLDER -->", reward_html)
    
    # --- おすすめタスクの生成 ---
    prices = fetch_market_prices()
    
    # 最高効率のアイテムを導出 (売れ行きを考慮)
    max_score = 0.0
    max_efficiency = 0.0
    best_item_name = ""
    best_velocity = 0.0
    for cat in COSMO_CREDIT_DATA:
        for item in cat['items']:
            item_data = prices.get(item.get('id', 0), {})
            market_price_str = item_data.get('price', '---') if isinstance(item_data, dict) else '---'
            try:
                velocity = float(item_data.get('velocity') or 0.0) if isinstance(item_data, dict) else 0.0
            except:
                velocity = 0.0
            
            if market_price_str != "---":
                try:
                    gil = int(market_price_str.replace(',', ''))
                    credit = int(item['price'].replace(',', ''))
                    if credit > 0:
                        eff = gil / credit
                        # 売れ行き(1日あたりの平均販売数)をスコアに加味
                        # velocityが1.0以上なら満点、それ以下ならペナルティを課す
                        safe_velocity = max(velocity, 0.01)
                        weight = min(1.0, safe_velocity / 1.0)
                        score = eff * weight
                        
                        if score > max_score:
                            max_score = score
                            max_efficiency = eff # 実際の換金効率は生のまま保持
                            best_item_name = item['name']
                            best_velocity = velocity
                except:
                    pass

    now_dt = datetime.now()
    now_m = now_dt.minute
    
    op_mins = [16, 36, 56]
    next_op = next((m for m in op_mins if m >= now_m), None)
    if next_op is None:
        next_op = 16
        min_to_op = (60 - now_m) + 16
    else:
        min_to_op = next_op - now_m

    recommend_html = "<ul style='color: #e2f1f8; font-size: 14px; line-height: 1.6; padding-left: 20px; margin: 0;'>"
    if max_efficiency > 0:
        vel_text = "売れ行き良好" if best_velocity >= 1.0 else "売れ行き低め"
        recommend_html += f"<li style='margin-bottom: 15px; list-style-type: none; margin-left: -20px;'><div style='background: rgba(247, 206, 85, 0.1); border: 1px solid rgba(247, 206, 85, 0.3); padding: 10px; border-radius: 6px;'><span style='color: #f7ce55; font-weight: bold;'>💰 現在の最高金策アイテム:</span> <strong>{best_item_name}</strong> (1コスモクレジットあたり約 <span style='color: #f7ce55;'>{max_efficiency:.1f} gil</span> / <span style='color: #f7ce55;'>{vel_text}</span>)<br><span style='font-size: 11px; color: #8da1b5; display: inline-block; margin-top: 5px; line-height: 1.4;'>※価格だけでなく、直近50件の取引履歴から「1日あたりの平均販売数(速)」を算出し、スコア化して選出しています。<br>1日に1個以上売れているアイテムは健全とし、それ未満のものは売れないリスクがあるとして評価を下げ、『実際にギルにしやすく価格も高い』アイテムを優先して表示します。</span></div></li>"

    gil_mecha = f"{int(1800 * max_efficiency):,}" if max_efficiency > 0 else "---"
    gil_ex = f"{int(50 * max_efficiency):,}" if max_efficiency > 0 else "---"
    
    next_op_str = f"LT毎時{next_op:02d}分"
    
    if min_to_op == 0:
        recommend_html += f"<li><span style='color: #f7ce55; font-weight: bold;'>【最優先】</span>ただいまメカオペ ({next_op_str}) が開催中です！ パエンナ/オイジュスクレジットが1000個以上ある場合は急いで参加しましょう！<br><span style='font-size: 12px; color: #f7ce55;'>(※参加で1800コスモクレジット獲得 → 実質約 <strong>{gil_mecha} gil</strong> 相当)</span></li>"
    elif min_to_op <= 5:
        recommend_html += f"<li><span style='color: #f7ce55; font-weight: bold;'>【最優先】</span>まもなくメカオペ ({next_op_str} / {min_to_op}分後) が開催されます！パエンナ/オイジュスクレジットが1000個以上ある場合は参加を最優先しましょう。<br><span style='font-size: 12px; color: #f7ce55;'>(※参加で1800コスモクレジット獲得 → 実質約 <strong>{gil_mecha} gil</strong> 相当)</span></li>"
    else:
        recommend_html += f"<li><span style='color: #4ed8d1; font-weight: bold;'>【準備】</span>次のメカオペは {next_op_str} ({min_to_op}分後) です。メカオペ参加費の「パエンナクレジット」または「オイジュスクレジット」を優先して1000個集めましょう。<br><span style='font-size: 12px; color: #4ed8d1;'>(※参加で1800コスモクレジット獲得 → 実質約 {gil_mecha} gil 相当)</span></li>"


    # アクティブな高ランクミッションを探す
    active_ex_crafter = []
    active_a_crafter = []
    active_ex_gatherer = []
    active_a_gatherer = []
    
    # 指定された6クラスのみを対象とする
    allowed_gatherers = ["採掘師", "園芸師", "漁師"]
    allowed_crafters = ["革細工師", "彫金師", "錬金術師"]
    
    for mdata in MISSION_DATA:
        area = mdata['area']
        area_short = area.split('（')[0] if '（' in area else area
        for row in mdata['schedule']:
            time_str = row['time'].replace('ET ', '')
            time_parts = time_str.split('～')
            if len(time_parts) == 2:
                start_h = int(time_parts[0].split(':')[0])
                end_h = int(time_parts[1].split(':')[0])
                if time_parts[1].endswith('59'):
                    end_h += 1
                
                if start_h < end_h:
                    is_act = (start_h <= now_et_hour < end_h)
                else:
                    is_act = (now_et_hour >= start_h or now_et_hour < end_h)
                    
                if is_act:
                    mission_name = row['mission']
                    
                    # 対象クラスの判定
                    is_gatherer = any(gj in mission_name for gj in allowed_gatherers)
                    is_crafter = any(cj in mission_name for cj in allowed_crafters)
                    
                    if is_gatherer or is_crafter:
                        if "EX+" in mission_name:
                            if is_gatherer:
                                active_ex_gatherer.append(f"{area_short} ({mission_name})")
                            else:
                                active_ex_crafter.append(f"{area_short} ({mission_name})")
                        elif "A" in mission_name:
                            if is_gatherer:
                                active_a_gatherer.append(f"{area_short} ({mission_name})")
                            else:
                                active_a_crafter.append(f"{area_short} ({mission_name})")

    # クラフター向け提案
    recommend_html += "<li style='margin-top: 15px;'><strong style='color: #e2f1f8;'>【クラフター (革・彫・錬)】金策タスク:</strong><br>"
    if active_ex_crafter:
        recommend_html += f"<span style='color: #f7ce55;'>EX+発生中:</span> <span style='color: #8da1b5; font-size: 13px;'>{', '.join(active_ex_crafter)}</span><br><span style='font-size: 11px; color: #f7ce55;'>(※1回あたり約50コスモクレジット獲得想定 → 実質約 {gil_ex} gil 相当)</span>"
    elif active_a_crafter:
        recommend_html += f"<span style='color: #4ed8d1;'>Aランク発生中:</span> <span style='color: #8da1b5; font-size: 13px;'>{', '.join(active_a_crafter)}</span>"
    else:
        recommend_html += "<span style='color: #5a6e7c; font-size: 13px;'>現在高ランクの時限ミッションはありません。</span>"
    recommend_html += "</li>"

    # ギャザラー向け提案
    recommend_html += "<li style='margin-top: 10px;'><strong style='color: #e2f1f8;'>【ギャザラー (採・園・漁)】金策タスク:</strong><br>"
    if active_ex_gatherer:
        recommend_html += f"<span style='color: #f7ce55;'>EX+発生中:</span> <span style='color: #8da1b5; font-size: 13px;'>{', '.join(active_ex_gatherer)}</span><br><span style='font-size: 11px; color: #f7ce55;'>(※1回あたり約50コスモクレジット獲得想定 → 実質約 {gil_ex} gil 相当)</span>"
    elif active_a_gatherer:
        recommend_html += f"<span style='color: #4ed8d1;'>Aランク発生中:</span> <span style='color: #8da1b5; font-size: 13px;'>{', '.join(active_a_gatherer)}</span>"
    else:
        recommend_html += "<span style='color: #5a6e7c; font-size: 13px;'>現在高ランクの時限ミッションはありません。</span>"
    # --- オイジュス・エネルギーパックの比較ロジック ---
    pack_data = prices.get(50414, {})
    pack_price_str = pack_data.get('price', '---')
    jidan_data = prices.get(50334, {})
    jidan_price_str = jidan_data.get('price', '---')
    face_data = prices.get(50435, {})
    face_price_str = face_data.get('price', '---')
    
    analysis_html = ""
    if pack_price_str != "---" and jidan_price_str != "---" and face_price_str != "---":
        pack_price = int(pack_price_str.replace(',', ''))
        jidan_price = int(jidan_price_str.replace(',', ''))
        face_price = int(face_price_str.replace(',', ''))
        
        # 期待値計算 (5%で当選枠を引き、その中でさらに各確率で抽選される二段構え)
        # 画像統計に基づき、地団駄 6.89% / フェイス鍵 6.21% で計算
        ev = 0.05 * ( (jidan_price * 0.0689) + (face_price * 0.0621) )
        diff = ev - pack_price
        
        advice = ""
        if diff > 0:
            advice = f"<span style='color: #f7ce55; font-weight: bold;'>【開封推奨】</span> 期待値が売却額を <strong>{int(diff):,} gil</strong> 上回っています。使って夢を見ましょう！"
        else:
            advice = f"<span style='color: #4ed8d1; font-weight: bold;'>【売却推奨】</span> 期待値が売却額を <strong>{int(abs(diff)):,} gil</strong> 下回っています。そのまま売るのが堅実です。"
            
        analysis_html = f"""
        <li style='margin-top: 15px; list-style-type: none; margin-left: -20px;'>
            <div style='background: rgba(78, 216, 209, 0.1); border: 1px solid rgba(78, 216, 209, 0.3); padding: 10px; border-radius: 6px;'>
                <strong style='color: #e2f1f8;'>📦 オイジュス・エネルギーパック鑑定:</strong><br>
                <div style='font-size: 13px; margin: 5px 0;'>
                    現物売却: <span style='color: #f7ce55;'>{pack_price_str} gil</span><br>
                    開封期待値: <span style='color: #f7ce55;'>{int(ev):,} gil</span> (5%当選枠内 → 各種抽選)
                </div>
                <div style='font-size: 12px;'>{advice}</div>
            </div>
        </li>
        """
    
    recommend_html += analysis_html
    recommend_html += "</ul>"
    
    html_template = html_template.replace("<!-- RECOMMENDATION_PLACEHOLDER -->", recommend_html)
    
    # --- コスモクレジット一覧の生成 ---
    credit_html = ""
    for cat in COSMO_CREDIT_DATA:
        credit_html += f"""
            <div class="credit-category">
                <div class="credit-category-title">{cat['category']}</div>
                <table class="credit-table">
                    <tr>
                        <th style="text-align: left; padding-bottom: 5px; color: #8da1b5; font-size: 10px;">アイテム名</th>
                        <th style="text-align: right; padding-bottom: 5px; color: #8da1b5; font-size: 10px;">クレジット</th>
                        <th style="text-align: right; padding-bottom: 5px; color: #3cb8f6; font-size: 10px;">最安値 (JP)</th>
                        <th style="text-align: right; padding-bottom: 5px; color: #f7ce55; font-size: 10px;">単価(gil/コスモクレジット)</th>
                    </tr>
        """
        for item in cat['items']:
            item_data = prices.get(item.get('id', 0), {})
            market_price_str = item_data.get('price', '---') if isinstance(item_data, dict) else '---'
            try:
                velocity = float(item_data.get('velocity') or 0.0) if isinstance(item_data, dict) else 0.0
            except:
                velocity = 0.0
            
            price_style = "color: #3cb8f6;" if market_price_str != "---" else "color: #5a6e7c;"
            
            # 1クレジットあたりのギル計算
            efficiency = "---"
            if market_price_str != "---":
                try:
                    # "180,000" -> 180000
                    gil = int(market_price_str.replace(',', ''))
                    # "8,400" -> 8400
                    credit = int(item['price'].replace(',', ''))
                    if credit > 0:
                        efficiency = f"{gil / credit:.1f}"
                except:
                    pass
            
            credit_html += f"""
                    <tr>
                        <td class="item-name">{item['name']}</td>
                        <td class="item-price">{item['price']} <span class="credit-icon">コスモクレジット</span></td>
                        <td class="item-price" style="{price_style}">{market_price_str} <span style="font-size:9px;">gil</span> <span style="color:#5a6e7c;font-size:9px;">(速:{velocity:.1f})</span></td>
                        <td class="item-price" style="color: #f7ce55;">{efficiency}</td>
                    </tr>
            """
        credit_html += "                </table>\n            </div>"
    
    html_template = html_template.replace("<!-- CREDIT_PLACEHOLDER -->", credit_html)
    
    # --- レア/高額アイテム一覧の生成 ---
    rare_html = """
        <table class="credit-table">
            <tr>
                <th style="text-align: left; padding-bottom: 5px; color: #8da1b5; font-size: 10px;">アイテム名</th>
                <th style="text-align: right; padding-bottom: 5px; color: #f7ce55; font-size: 10px;">最安値 (JP)</th>
            </tr>
    """
    for item in RARE_ITEMS_DATA:
        item_data = prices.get(item['id'], {})
        market_price_str = item_data.get('price', '---') if isinstance(item_data, dict) else '---'
        price_style = "color: #f7ce55; font-weight: bold;" if market_price_str != "---" else "color: #5a6e7c;"
        
        rare_html += f"""
            <tr>
                <td class="item-name" style="color: #e2f1f8;">{item['name']}</td>
                <td class="item-price" style="{price_style}">{market_price_str} <span style="font-size:9px;">gil</span></td>
            </tr>
        """
    rare_html += "</table>"
    
    html_template = html_template.replace("<!-- RARE_ITEMS_PLACEHOLDER -->", rare_html)
    
    return html_template

class WeatherRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            
            # アクセスされるたびに最新の天気を計算してHTMLを返す
            forecasts = generate_forecast()
            html_content = generate_html(forecasts)
            
            self.wfile.write(html_content.encode('utf-8'))
        elif self.path == '/static/style.css':
            # CSSファイルを読み込んで返す
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            with open('static/style.css', 'rb') as f:
                self.wfile.write(f.read())
        else:
            super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), WeatherRequestHandler) as httpd:
        print(f"✅ サーバーを起動しました。ブラウザで http://localhost:{PORT} にアクセスしてください。")
        print("💡 終了するには Ctrl+C を押してください。")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        print("サーバーを停止しました。")
