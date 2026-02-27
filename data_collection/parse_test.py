import re

log_content = """
[20:34] 2ゴールドカウントにより、報酬量が5%増加した！
[20:34] コスモクレジット×131(+6)を手に入れた。
[20:34] オイジュスクレジット×120(+35)を手に入れた。
[20:34] オイジュス・ドローンチップ×113(+5)を手に入れた。
[20:34] 園芸師の技巧点を820点獲得した！
"""

for line in log_content.strip().split('\n'):
    credit_match = re.search(r'コスモクレジット×(\d+)(?:\(\+(\d+)\))?', line)
    if credit_match:
        total = int(credit_match.group(1))
        bonus = int(credit_match.group(2)) if credit_match.group(2) else 0
        base = total - bonus
        print(f"Cosmo Credit -> Base: {base}, Bonus: {bonus}, Total: {total}")
    
    oj_credit_match = re.search(r'オイジュスクレジット×(\d+)(?:\(\+(\d+)\))?', line)
    if oj_credit_match:
        total = int(oj_credit_match.group(1))
        bonus = int(oj_credit_match.group(2)) if oj_credit_match.group(2) else 0
        base = total - bonus
        print(f"Ojus Credit -> Base: {base}, Bonus: {bonus}, Total: {total}")
        
    gold_count_match = re.search(r'(\d+)ゴールドカウント', line)
    if gold_count_match:
        print(f"Gold Count Tier -> {gold_count_match.group(1)}")
