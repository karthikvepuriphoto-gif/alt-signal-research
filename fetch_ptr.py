import sys, os, json, time, subprocess
sys.path.insert(0,"/workspace/day-trader-skill/trader-pelosi"); import ptr
from concurrent.futures import ThreadPoolExecutor
rows_all=[]
for y in range(2019,2027):
    try: idx=ptr.load_index(y)
    except Exception as e: print("idx fail",y,e); continue
    P=[r for r in idx if r.get("filing_type")=="P" or r.get("type")=="P" or r.get("FilingType")=="P"]
    print(y,len(idx),len(P), idx[0] if idx else None, flush=True)
    for r in P: r["year"]=y
    rows_all+=P
json.dump(rows_all,open("data/ptr/index.json","w"),default=str)
def get(r):
    doc=r.get("doc_id") or r.get("DocID"); y=r["year"]; txt=f"data/ptr/{doc}.txt"
    if os.path.exists(txt): return
    pdf=f"data/ptr/{doc}.pdf"
    try:
        b=ptr.download(ptr.PTR_URL%(y,doc)); open(pdf,"wb").write(b)
        subprocess.run(["pdftotext","-layout",pdf,txt],timeout=60); os.remove(pdf)
    except Exception as e: open(txt,"w").write("")
with ThreadPoolExecutor(4) as ex: list(ex.map(get,rows_all))
print("DONE")
