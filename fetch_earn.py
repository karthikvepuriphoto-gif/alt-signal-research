import yfinance as yf, pandas as pd, os, time, warnings; warnings.filterwarnings("ignore")
from concurrent.futures import ThreadPoolExecutor
T=list(pd.read_parquet("data/eq_adj.parquet").columns)
def f(t):
    p=f"data/earn/{t}.csv"
    if os.path.exists(p): return
    for k in range(3):
        try:
            e=yf.Ticker(t).get_earnings_dates(limit=100)
            if e is not None: e.to_csv(p); return
        except Exception as ex: time.sleep(5*(k+1))
    open(p,"w").write("")
with ThreadPoolExecutor(3) as ex: list(ex.map(f,T))
print("DONE")
