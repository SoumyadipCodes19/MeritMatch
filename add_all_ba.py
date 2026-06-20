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
prog_buffer = []

for i in range(1, len(df)):
    c = str(df.iloc[i, 1]).strip() if pd.notna(df.iloc[i, 1]) else ''
    p = str(df.iloc[i, 2]).strip() if pd.notna(df.iloc[i, 2]) else ''
    
    if c and c not in ['COLLEGE NAME', 'S.NO.', 'nan', 'NAME OF THE COLLEGE']:
        current_col = c
    
    has_score = False
    for j in range(3, 9):
        if pd.notna(df.iloc[i, j]) and str(df.iloc[i, j]).strip() not in ['', '-']:
            has_score = True
            break
            
    if p and p not in ['PROGRAM NAME', 'NAME OF THE PROGRAM']:
        prog_buffer.append(p)
        
    if has_score:
        full_prog = ' '.join(prog_buffer).strip()
        if 'Prog' in full_prog and 'B.A' in full_prog and current_col:
            entry = get_or_create(current_col, full_prog)
            for j, cat in enumerate(cats):
                val = df.iloc[i, 3 + j]
                try:
                    v = float(val)
                    if not math.isnan(v): entry['r1'][cat] = v
                except:
                    pass
        prog_buffer = []

# --- ROUND 3 ---
current_col = None
prog_buffer = []

for i in range(1, len(df)):
    c = str(df.iloc[i, 11]).strip() if pd.notna(df.iloc[i, 11]) else ''
    p = str(df.iloc[i, 12]).strip() if pd.notna(df.iloc[i, 12]) else ''
    
    if c and c not in ['COLLEGE NAME', 'S.NO.', 'nan', 'NAME OF THE COLLEGE']:
        current_col = c
    
    has_score = False
    for j in range(13, 19):
        if pd.notna(df.iloc[i, j]) and str(df.iloc[i, j]).strip() not in ['', '-']:
            has_score = True
            break
            
    if p and p not in ['PROGRAM NAME', 'NAME OF THE PROGRAM']:
        prog_buffer.append(p)
        
    if has_score:
        full_prog = ' '.join(prog_buffer).strip()
        if 'Prog' in full_prog and 'B.A' in full_prog and current_col:
            entry = get_or_create(current_col, full_prog)
            for j, cat in enumerate(cats):
                val = df.iloc[i, 13 + j]
                try:
                    v = float(val)
                    if not math.isnan(v): entry['r3'][cat] = v
                except:
                    pass
        prog_buffer = []

# --- SPOT ROUND ---
for i in range(1, len(df)):
    p = str(df.iloc[i, 21]).strip() if pd.notna(df.iloc[i, 21]) else ''
    c = str(df.iloc[i, 22]).strip() if pd.notna(df.iloc[i, 22]) else ''
    cat = str(df.iloc[i, 23]).strip() if pd.notna(df.iloc[i, 23]) else ''
    val = df.iloc[i, 24]
    
    if 'Prog' in p and 'B.A' in p and c and cat in cats:
        entry = get_or_create(c, p)
        try:
            v = float(val)
            if not math.isnan(v): entry['spot'][cat] = v
        except:
            pass

# Now load JSON and add
with open('cutoff_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filter out old BA Programs to prevent dupes
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

print(f'Successfully added {len(results)} B.A. Program combinations!')
