import json
import pandas as pd
import math

df = pd.read_excel('DU Round 1, Round 3, Spot Round.xlsx', sheet_name='Sheet1', header=None)

results = {} # key: (college, prog) -> { 'r1': {...}, 'r3': {...}, 'spot': {...} }
cats = ['UR', 'OBC', 'SC', 'ST', 'EWS', 'PwBD']

def get_or_create(c, p):
    if (c, p) not in results:
        results[(c, p)] = {'r1': {k: None for k in cats}, 'r3': {k: None for k in cats}, 'spot': {k: None for k in cats}}
    return results[(c, p)]

# --- ROUND 1 ---
current_col = None
current_prog = ''
current_scores = {cat: None for cat in cats}
last_col_when_started = None

for i in range(1, len(df)):
    c = str(df.iloc[i, 1]).strip() if pd.notna(df.iloc[i, 1]) else ''
    p = str(df.iloc[i, 2]).strip() if pd.notna(df.iloc[i, 2]) else ''
    
    if c and c not in ['COLLEGE NAME', 'S.NO.', 'nan', 'NAME OF THE COLLEGE']:
        if c in ['(Evening)', '(W)', 'College', 'Commerce', 'For Women (W)', 'Women (W)']:
            current_col += ' ' + c
        else:
            current_col = c
        
    is_new_prog = False
    if p and p != 'nan':
        if p.startswith('B.') or p.startswith('Bachelor') or p.startswith('Five') or p.startswith('PROGRAM'):
            is_new_prog = True
            
    if is_new_prog:
        if current_prog and 'B.A' in current_prog and 'Prog' in current_prog:
            if any(current_scores[cat] is not None for cat in cats):
                entry = get_or_create(last_col_when_started, current_prog)
                for cat in cats:
                    if current_scores[cat] is not None:
                        entry['r1'][cat] = current_scores[cat]
        current_prog = p
        current_scores = {cat: None for cat in cats}
        last_col_when_started = current_col
    elif p and p != 'nan':
        current_prog += ' ' + p
        
    for j, cat in enumerate(cats):
        val = df.iloc[i, 3+j]
        try:
            v = float(val)
            if not math.isnan(v): current_scores[cat] = v
        except:
            pass

# final flush r1
if current_prog and 'B.A' in current_prog and 'Prog' in current_prog:
    if any(current_scores[cat] is not None for cat in cats):
        entry = get_or_create(last_col_when_started, current_prog)
        for cat in cats:
            if current_scores[cat] is not None:
                entry['r1'][cat] = current_scores[cat]


# --- ROUND 3 ---
current_col = None
current_prog = ''
current_scores = {cat: None for cat in cats}
last_col_when_started = None

for i in range(1, len(df)):
    c = str(df.iloc[i, 11]).strip() if pd.notna(df.iloc[i, 11]) else ''
    p = str(df.iloc[i, 12]).strip() if pd.notna(df.iloc[i, 12]) else ''
    
    if c and c not in ['COLLEGE NAME', 'S.NO.', 'nan', 'NAME OF THE COLLEGE']:
        if c in ['(Evening)', '(W)', 'College', 'Commerce', 'For Women (W)', 'Women (W)']:
            current_col += ' ' + c
        else:
            current_col = c
        
    is_new_prog = False
    if p and p != 'nan':
        if p.startswith('B.') or p.startswith('Bachelor') or p.startswith('Five') or p.startswith('PROGRAM'):
            is_new_prog = True
            
    if is_new_prog:
        if current_prog and 'B.A' in current_prog and 'Prog' in current_prog:
            if any(current_scores[cat] is not None for cat in cats):
                entry = get_or_create(last_col_when_started, current_prog)
                for cat in cats:
                    if current_scores[cat] is not None:
                        entry['r3'][cat] = current_scores[cat]
        current_prog = p
        current_scores = {cat: None for cat in cats}
        last_col_when_started = current_col
    elif p and p != 'nan':
        current_prog += ' ' + p
        
    for j, cat in enumerate(cats):
        val = df.iloc[i, 13+j]
        try:
            v = float(val)
            if not math.isnan(v): current_scores[cat] = v
        except:
            pass

# final flush r3
if current_prog and 'B.A' in current_prog and 'Prog' in current_prog:
    if any(current_scores[cat] is not None for cat in cats):
        entry = get_or_create(last_col_when_started, current_prog)
        for cat in cats:
            if current_scores[cat] is not None:
                entry['r3'][cat] = current_scores[cat]


# --- SPOT ROUND ---
spot_current_col = None
for i in range(1, len(df)):
    p = str(df.iloc[i, 21]).strip() if pd.notna(df.iloc[i, 21]) else ''
    c = str(df.iloc[i, 22]).strip() if pd.notna(df.iloc[i, 22]) else ''
    cat = str(df.iloc[i, 23]).strip() if pd.notna(df.iloc[i, 23]) else ''
    val = df.iloc[i, 24]
    
    if c and c not in ['COLLEGE NAME', 'S.NO.', 'nan', 'NAME OF THE COLLEGE']:
        if c in ['(Evening)', '(W)', 'College', 'Commerce', 'For Women (W)', 'Women (W)']:
            if spot_current_col:
                spot_current_col += ' ' + c
        else:
            spot_current_col = c
            
    if 'Prog' in p and 'B.A' in p and spot_current_col and cat in cats:
        entry = get_or_create(spot_current_col, p)
        try:
            v = float(val)
            if not math.isnan(v): entry['spot'][cat] = v
        except:
            pass


# Now load JSON and add
with open('cutoff_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filter out all BA Programs to start fresh
data = [item for item in data if not ('Prog' in item['course'] and 'B.A' in item['course'])]

max_sno = max(item['sno'] for item in data) if data else 0

def get_campus(college_name):
    lower = college_name.lower()
    if 'south' in lower or 'venkateswara' in lower or 'ram lal anand' in lower or 'aryabhatta' in lower or 'motilal' in lower or 'gargi' in lower or 'kamala' in lower or 'dyal' in lower or 'bhagat' in lower:
        return 'South Campus'
    if 'north' in lower or 'stephen' in lower or 'hindu' in lower or 'hansraj' in lower or 'kirori' in lower or 'miranda' in lower or 'ramjas' in lower or 'khalsa' in lower:
        return 'North Campus'
    return 'Off Campus'

for (c, p), scores in results.items():
    norm_p = p.replace('B.A Program', 'B.A. Program').replace('B.A. (Prog.)', 'B.A. Program')
    
    max_sno += 1
    new_entry = {
        'sno': max_sno,
        'college': c,
        'course': norm_p,
        'merit': 'Type 6', # B.A Program falls under Type 6
        'campus': get_campus(c),
        'is_evening': '(evening)' in c.lower() or ' evening' in c.lower(),
        'cutoffs': scores
    }
    data.append(new_entry)

with open('cutoff_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f)
with open('data.js', 'w', encoding='utf-8') as f:
    f.write('const CUTOFF_DATA = ' + json.dumps(data) + ';')

print(f'Successfully added {len(results)} clean B.A. Program combinations!')
