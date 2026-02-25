import os
import time
import math
import json
import urllib.request
import threading
from datetime import datetime
import http.server
import socketserver
from EorzeaEnv import EorzeaWeather, EorzeaLang
import re

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
            {"name": "ポートレート教材:コスモエクスプローラー1", "price": "6,000", "id": 48091},
            {"name": "ポートレート教材:コスモエクスプローラー2", "price": "6,000", "id": 46768},
            {"name": "ポートレート教材:コスモエクスプローラー3", "price": "6,000", "id": 50019},
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
            {"name": "黄金の霊砂", "price": "200", "id": 44035},
            {"name": "幻岩の霊砂", "price": "400", "id": 44036},
            {"name": "幻葉の霊砂", "price": "400", "id": 44037},
            {"name": "幻海の霊砂", "price": "400", "id": 44038},
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
CACHE_DURATION = 300 # 5分おきに更新

def market_price_worker():
    """バックグラウンドでマーケット価格を定期更新するスレッド"""
    global MARKET_PRICE_CACHE
    
    while True:
        try:
            item_ids = []
            for cat in COSMO_CREDIT_DATA:
                for item in cat['items']:
                    if 'id' in item:
                        item_ids.append(str(item['id']))
            
            for item in RARE_ITEMS_DATA:
                item_ids.append(str(item['id']))
            
            if not item_ids:
                time.sleep(60)
                continue
                
            # Universalis API (Japan Region) - 負荷軽減のため10件ずつ分割して取得
            new_cache = {}
            chunk_size = 10
            for i in range(0, len(item_ids), chunk_size):
                chunk = item_ids[i:i + chunk_size]
                item_ids_str = ",".join(chunk)
                url = f"https://universalis.app/api/v2/Japan/{item_ids_str}?listings=0&entries=1"
                
                req = urllib.request.Request(url, headers={'User-Agent': 'FF14_Dashboard/1.0'})
                try:
                    with urllib.request.urlopen(req, timeout=15) as response:
                        data = json.loads(response.read().decode())
                        
                        items = data.get('items', {})
                        if not items and 'itemID' in data:
                            items = {str(data['itemID']): data}

                        for iid_str, idata in items.items():
                            price = idata.get('minPrice')
                            n_price = idata.get('minPriceNQ')
                            h_price = idata.get('minPriceHQ')
                            
                            final_price = price or n_price or h_price or 0
                            velocity = idata.get('regularSaleVelocity', 0)
                            
                            new_cache[int(iid_str)] = {
                                'price': f"{int(final_price):,}" if final_price > 0 else "---",
                                'velocity': velocity
                            }
                except Exception as chunk_er:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Chunk fetch error for {item_ids_str}: {chunk_er}")
                
                # APIへの負荷軽減のため少し待機
                time.sleep(0.5)
            
            if new_cache:
                MARKET_PRICE_CACHE = new_cache
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Market prices updated (Background, {len(new_cache)} items).")
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error in background price update loop: {e}")
            
        # 次の更新まで待機
        time.sleep(CACHE_DURATION)

def fetch_market_prices():
    """現在のキャッシュを即座に返す (API通信は行わない)"""
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
                weather_html += f"""                    <div class="result-item"><span class="result-time">{m['time_text']}</span> <span class="weather-badge">{m['weather']}</span></div>
"""
                
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
            try:
                item_data = prices.get(item.get('id', 0), {})
                market_price_str = item_data.get('price', '---') if isinstance(item_data, dict) else '---'
                raw_velocity = float(item_data.get('velocity', 1.0)) if isinstance(item_data, dict) else 1.0
                velocity = raw_velocity if raw_velocity > 0 else 1.0
                
                if market_price_str != "---":
                    gil = int(market_price_str.replace(',', ''))
                    credit_str = re.sub(r'[^0-9]', '', str(item.get('price', '0')))
                    credit = int(credit_str) if credit_str else 0
                    
                    if credit > 0:
                        eff = gil / credit
                        safe_velocity = max(velocity, 0.01)
                        weight = min(1.0, safe_velocity / 1.0)
                        score = eff * weight
                        print(f"DEBUG: {item['name']} - Gil:{gil}, Credit:{credit}, Eff:{eff:.2f}, Vel:{velocity}, Score:{score:.2f}")

                        if score > max_score:
                            max_score = score
                            max_efficiency = eff
                            best_item_name = item['name']
                            best_velocity = velocity
            except Exception as e:
                print(f"Error calculating item EV for {item.get('name', 'Unknown')}: {e}")

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
    if max_efficiency <= 0:
        max_efficiency = 25.0
        best_item_name = "エラー:相場取得不可 (25gil換算)"
        
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
    active_ex_crafter_areas = {}
    
    active_ex_gatherer = []
    active_a_gatherer = []
    active_ex_gatherer_areas = {}
    
    # 指定された6クラスのみを対象とする
    allowed_gatherers = ["採掘師", "園芸師", "漁師"]
    allowed_crafters = ["革細工師", "彫金師", "錬金術師"]
    
    # 報酬定数の設定
    AREA_TO_COSMO_RATIO = 1.8
    # マーケット価格の取得（証書、パック）
    cert_paenna_price = int(prices.get(47343, {}).get('price', '0').replace(',', '')) if prices.get(47343, {}).get('price', '0') != '---' else 0
    if cert_paenna_price == 0: cert_paenna_price = 100000

    cert_oizys_price = int(prices.get(50829, {}).get('price', '0').replace(',', '')) if prices.get(50829, {}).get('price', '0') != '---' else 0
    if cert_oizys_price == 0: cert_oizys_price = 200000

    pack_price = int(prices.get(50414, {}).get('price', '0').replace(',', '')) if prices.get(50414, {}).get('price', '0') != '---' else 0
    if pack_price == 0: pack_price = 15000

    # 報酬データ（固定値）に基づくEV計算用変数
    best_crafter_ev = 0
    best_crafter_job_type = ""
    best_crafter_breakdown = ""

    best_gatherer_ev = 0
    best_gatherer_job_type = ""
    best_gatherer_breakdown = ""

    for mdata in MISSION_DATA:
        area = mdata['area']
        area_short = area.split('（')[0] if '（' in area else area
        
        # 表示名の統一
        if "テンペスト" in area_short:
            area_disp = "オイジュス"
        elif "東ザナラーン" in area_short:
            area_disp = "パエンナ"
        elif "ウルティマ・トゥーレ" in area_short:
            area_disp = "焦がれの入り江"
        else:
            area_disp = area_short

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
                            # ジョブ特化型のEV計算
                            cosmo, local, manuals, chips = 0, 0, 0, 0
                            cert_pr = 0
                            
                            # エリア判定（元の文字列で判定）
                            if "パエンナ" in area:
                                cert_pr = cert_paenna_price
                                if is_crafter:
                                    cosmo, local, manuals, chips = 75, 50, 180, 0
                                else:
                                    cosmo, local, manuals, chips = 75, 50, 75, 0
                            elif "オイジュス" in area:
                                cert_pr = cert_oizys_price
                                if is_crafter:
                                    # クラフターの天候EX+の最大値を採用（234チップ、215手形）
                                    cosmo, local, manuals, chips = 65, 43, 215, 234
                                elif "漁師" in mission_name:
                                    cosmo, local, manuals, chips = 26, 17, 85, 107
                                else:
                                    # 採掘園芸
                                    cosmo, local, manuals, chips = 25, 17, 85, 108
                            elif "ウルティマ・トゥーレ" in area:
                                cert_pr = 0  # 証書なし
                                if is_crafter:
                                    cosmo, local, manuals, chips = 65, 43, 0, 0
                                elif "漁師" in mission_name:
                                    cosmo, local, manuals, chips = 26, 17, 0, 0
                                else:
                                    cosmo, local, manuals, chips = 25, 17, 0, 0

                            ev_credits = (cosmo + local * AREA_TO_COSMO_RATIO) * max_efficiency
                            ev_manuals = (manuals / 100.0) * cert_pr
                            ev_chips = (chips / 200.0) * pack_price
                            total_ev = ev_credits + ev_manuals + ev_chips
                            breakdown_str = f"クレ: {int(ev_credits):,} / 証書: {int(ev_manuals):,} / パック: {int(ev_chips):,}"
                            
                            short_job = mission_name.replace('EX+: ', '')
                            
                            if is_crafter:
                                if area_disp not in active_ex_crafter_areas:
                                    active_ex_crafter_areas[area_disp] = {'jobs': [], 'ev': total_ev, 'breakdown': breakdown_str}
                                if short_job not in active_ex_crafter_areas[area_disp]['jobs']:
                                    active_ex_crafter_areas[area_disp]['jobs'].append(short_job)
                                if total_ev > active_ex_crafter_areas[area_disp]['ev']:
                                    active_ex_crafter_areas[area_disp]['ev'] = total_ev
                                    active_ex_crafter_areas[area_disp]['breakdown'] = breakdown_str
                            else:
                                if area_disp not in active_ex_gatherer_areas:
                                    active_ex_gatherer_areas[area_disp] = {'jobs': [], 'ev': total_ev, 'breakdown': breakdown_str}
                                if short_job not in active_ex_gatherer_areas[area_disp]['jobs']:
                                    active_ex_gatherer_areas[area_disp]['jobs'].append(short_job)
                                if total_ev > active_ex_gatherer_areas[area_disp]['ev']:
                                    active_ex_gatherer_areas[area_disp]['ev'] = total_ev
                                    active_ex_gatherer_areas[area_disp]['breakdown'] = breakdown_str

                        elif "A" in mission_name:
                            if is_gatherer:
                                active_a_gatherer.append(f"{area_disp} ({mission_name})")
                            else:
                                active_a_crafter.append(f"{area_disp} ({mission_name})")

    # 妥協案（通常EX）の計算
    fallback_crafter_ev = ((22 + 13 * AREA_TO_COSMO_RATIO) * max_efficiency) + ((57 / 200.0) * pack_price)
    fallback_crafter_breakdown = f"クレ: {int((22 + 13 * AREA_TO_COSMO_RATIO) * max_efficiency):,} / 証書: 0 / パック: {int((57 / 200.0) * pack_price):,}"

    fallback_gatherer_ev = ((18 + 11 * AREA_TO_COSMO_RATIO) * max_efficiency) + ((49 / 200.0) * pack_price)
    fallback_gatherer_breakdown = f"クレ: {int((18 + 11 * AREA_TO_COSMO_RATIO) * max_efficiency):,} / 証書: 0 / パック: {int((49 / 200.0) * pack_price):,}"

    # クラフター向け提案
    recommend_html += "<li style='margin-top: 15px;'><strong style='color: #e2f1f8;'>【クラフター (革・彫・錬)】金策タスク:</strong><br>"
    if active_ex_crafter_areas:
        job_disps = [f"{a} (EX+: {', '.join(d['jobs'])})" for a, d in active_ex_crafter_areas.items()]
        recommend_html += f"<span style='color: #f7ce55;'>EX+発生中:</span> <span style='color: #8da1b5; font-size: 13px;'>{', '.join(job_disps)}</span><br>"
        for a, d in active_ex_crafter_areas.items():
            recommend_html += f"<span style='font-size: 11px; color: #f7ce55;'>(※1回あたり クラフター({a}) 最大報酬想定 → 実質約 <strong>{int(d['ev']):,} gil</strong> 相当)</span><br>"
            recommend_html += f"<span style='font-size: 10px; color: #8da1b5; margin-left: 15px;'>[内訳] {d['breakdown']}</span><br>"
    elif active_a_crafter:
        recommend_html += f"<span style='color: #4ed8d1;'>Aランク発生中:</span> <span style='color: #8da1b5; font-size: 13px;'>{', '.join(active_a_crafter)}</span>"
    else:
        recommend_html += "<span style='color: #5a6e7c; font-size: 13px;'>現在高ランクの時限ミッションはありません。</span><br>"
        recommend_html += f"<span style='color: #8da1b5; font-size: 13px; margin-top: 4px; display: inline-block;'>💡妥協案 (いつでも可能): <strong>オイジュス 通常EXミッション</strong></span><br>"
        recommend_html += f"<span style='font-size: 11px; color: #8da1b5;'>(※1回あたり クラフター(通常EX) 報酬想定 → 実質約 <strong>{int(fallback_crafter_ev):,} gil</strong> 相当)</span><br>"
        recommend_html += f"<span style='font-size: 10px; color: #8da1b5; margin-left: 15px;'>[内訳] {fallback_crafter_breakdown}</span>"
    recommend_html += "</li>"

    # ギャザラー向け提案
    recommend_html += "<li style='margin-top: 10px;'><strong style='color: #e2f1f8;'>【ギャザラー (採・園・漁)】金策タスク:</strong><br>"
    if active_ex_gatherer_areas:
        job_disps = [f"{a} (EX+: {', '.join(d['jobs'])})" for a, d in active_ex_gatherer_areas.items()]
        recommend_html += f"<span style='color: #f7ce55;'>EX+発生中:</span> <span style='color: #8da1b5; font-size: 13px;'>{', '.join(job_disps)}</span><br>"
        for a, d in active_ex_gatherer_areas.items():
            recommend_html += f"<span style='font-size: 11px; color: #f7ce55;'>(※1回あたり ギャザラー({a}) 最大報酬想定 → 実質約 <strong>{int(d['ev']):,} gil</strong> 相当)</span><br>"
            recommend_html += f"<span style='font-size: 10px; color: #8da1b5; margin-left: 15px;'>[内訳] {d['breakdown']}</span><br>"
    elif active_a_gatherer:
        recommend_html += f"<span style='color: #4ed8d1;'>Aランク発生中:</span> <span style='color: #8da1b5; font-size: 13px;'>{', '.join(active_a_gatherer)}</span>"
    else:
        recommend_html += "<span style='color: #5a6e7c; font-size: 13px;'>現在高ランクの時限ミッションはありません。</span><br>"
        recommend_html += f"<span style='color: #8da1b5; font-size: 13px; margin-top: 4px; display: inline-block;'>💡妥協案 (いつでも可能): <strong>オイジュス 通常EXミッション</strong></span><br>"
        recommend_html += f"<span style='font-size: 11px; color: #8da1b5;'>(※1回あたり ギャザラー(通常EX) 報酬想定 → 実質約 <strong>{int(fallback_gatherer_ev):,} gil</strong> 相当)</span><br>"
        recommend_html += f"<span style='font-size: 10px; color: #8da1b5; margin-left: 15px;'>[内訳] {fallback_gatherer_breakdown}</span>"
    recommend_html += "</li>"
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
        base_ev = 0.05 * ( (jidan_price * 0.0689) + (face_price * 0.0621) )
        
        # 鑑定にかかる1分の拘束時間コスト（ダッシュボード最高効率アイテムのレートと連動）
        # 1分間あたり約500コスモクレジット相当の労働（機会損失）と定義して算出
        TIME_COST_1MIN = 500 * max_efficiency 
        ev = base_ev - TIME_COST_1MIN
        
        diff = ev - pack_price
        
        advice = ""
        if diff > 0:
            advice = f"<span style='color: #f7ce55; font-weight: bold;'>【開封推奨】</span> 実質期待値が売却額を <strong>{int(diff):,} gil</strong> 上回っています。使って夢を見ましょう！"
        else:
            advice = f"<span style='color: #4ed8d1; font-weight: bold;'>【売却推奨】</span> 鑑定の1分間拘束コストを考慮すると、そのまま売る方が <strong>{int(abs(diff)):,} gil</strong> お得です。"
            
        analysis_html = f"""
        <li style='margin-top: 15px; list-style-type: none; margin-left: -20px;'>
            <div style='background: rgba(78, 216, 209, 0.1); border: 1px solid rgba(78, 216, 209, 0.3); padding: 10px; border-radius: 6px;'>
                <strong style='color: #e2f1f8;'>📦 オイジュス・エネルギーパック鑑定:</strong><br>
                <div style='font-size: 13px; margin: 5px 0;'>
                    現物売却: <span style='color: #f7ce55;'>{pack_price_str} gil</span><br>
                    開封期待値: <span style='color: #8da1b5; text-decoration: line-through;'>{int(base_ev):,} gil</span> → <span style='color: #f7ce55; font-weight: bold;'>{int(ev):,} gil</span> <span style='font-size: 11px; color:#8da1b5;'>(※鑑定1分の拘束コスト: 現在の相場換算で -{int(TIME_COST_1MIN):,}gilを考慮)</span>
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

class WeatherRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/':
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
                    self.send_error(500, f"Error generating craft html: {e}")
                
            elif self.path == '/static/style.css':
                if os.path.exists('static/style.css'):
                    with open('static/style.css', 'rb') as f:
                        body = f.read()
                    self.send_response(200)
                    self.send_header("Content-type", "text/css")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_error(404, "File Not Found")
            else:
                super().do_GET()
                
        except Exception as e:
            # 詳細なエラー情報をコンソールに出力
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] !!! Server Error !!!: {e}")
            import traceback
            traceback.print_exc()
            # 既にヘッダーを送っていない場合のみ、500エラーを送信
            try:
                self.send_error(500, f"Internal Server Error: {e}")
            except:
                pass

def run_server():
    with socketserver.TCPServer(("", PORT), WeatherRequestHandler) as httpd:
        print(f"✅ サーバーを起動しました。ブラウザで http://localhost:{PORT} にアクセスしてください。")
        print("💡 終了するには Ctrl+C を押してください。")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        print("サーバーを停止しました。")

if __name__ == "__main__":
    # バックグラウンド更新スレッドの開始
    bg_thread = threading.Thread(target=market_price_worker, daemon=True)
    bg_thread.start()
    
    # サーバーの起動
    run_server()
