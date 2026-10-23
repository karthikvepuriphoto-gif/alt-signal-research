import requests, json, os, pandas as pd
from concurrent.futures import ThreadPoolExecutor
days=pd.date_range("2021-04-01","2026-10-22")
def f(d):
    p=f"data/wsb/{d:%Y-%m-%d}.json"
    if os.path.exists(p): return
    for _ in range(3):
        try:
            r=requests.get(f"https://tradestie.com/api/v1/apps/reddit?date={d:%m-%d-%Y}",timeout=60)
            if r.ok: open(p,"w").write(r.text); return
        except Exception: pass
with ThreadPoolExecutor(2) as ex: list(ex.map(f,days))
