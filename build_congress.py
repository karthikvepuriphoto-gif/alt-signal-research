import sys,json,os; sys.path.insert(0,'/workspace/day-trader-skill/trader-pelosi'); import ptr, pandas as pd
idx=json.load(open('data/ptr/index.json')); out=[]; ok=0; empty=0
for r in idx:
    p=f"data/ptr/{r['doc_id']}.txt"; t=open(p).read() if os.path.exists(p) else ''
    if not t.strip(): empty+=1; continue
    try: x=ptr.parse_ptr_text(t,filed=r['filed'])
    except Exception: continue
    ok+=1
    for row in x.get('rows',[]):
        out.append(dict(member=r['name'],doc=r['doc_id'],filed=x.get('filed') or r['filed'],trade=row.get('date'),type=row.get('type'),ticker=row.get('ticker'),lo=row.get('amount_low'),hi=row.get('amount_high'),late=row.get('late')))
d=pd.DataFrame(out); d.to_csv("data/congress_house_ptr_rows.csv",index=False)
print("docs parsed",ok,"empty/scanned",empty,"rows",len(d)); print(d.type.value_counts().head()); print(d.ticker.notna().mean())
