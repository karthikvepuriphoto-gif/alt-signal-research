import sys,glob,json,os; sys.path.insert(0,"lib")
from common import *; from events import calendar_time
import yfinance as yf
rows=[]
for f in sorted(glob.glob("data/wsb/*.json")):
    try: L=json.load(open(f))
    except Exception: continue
    for x in L: rows.append(dict(d=pd.Timestamp(os.path.basename(f)[:10]),sym=x["ticker"],c=x["no_of_comments"],sent=x["sentiment_score"]))
W=pd.DataFrame(rows); print("ticker-days",len(W),"days",W.d.nunique(),"tickers",W.sym.nunique())
# detect stale duplicates (identical consecutive snapshots)
snap=W.groupby("d").apply(lambda g: tuple(sorted(zip(g.sym,g.c)))); stale=snap.eq(snap.shift())
print("stale duplicate days",int(stale.sum())); W=W[~W.d.isin(stale[stale].index)]
C=W.pivot_table(index="d",columns="sym",values="c",aggfunc="sum")
C=C.reindex(pd.date_range(C.index.min(),C.index.max())).fillna(0)
base=C.rolling(20,min_periods=10).mean().shift(1)
syms=[s for s in C.columns if (C[s]>0).sum()>=3]
pp="data/wsb_prices.parquet"
if not os.path.exists(pp):
    px_=yf.download(syms+["SPY"],start="2021-03-01",auto_adjust=True,progress=False,threads=True)["Close"]; px_.to_parquet(pp)
px_=pd.read_parquet(pp); px_=px_.loc[:,px_.notna().sum()>100]
print("tickers with prices",px_.shape[1])
S=pd.DataFrame(W.pivot_table(index="d",columns="sym",values="sent",aggfunc="mean"))
out=[]
def ev(mask):
    e=mask.stack(); e=e[e]; return pd.DataFrame({"date":e.index.get_level_values(0),"sym":e.index.get_level_values(1)})
cs=[c for c in C.columns if c in px_.columns]
for k,minc in [(3,50),(5,100),(10,200)]:
    spike=(C[cs]>=minc)&(C[cs]>=k*base[cs].clip(lower=1))
    spike=spike&~spike.shift(1,fill_value=False)
    E=ev(spike)
    sb=S.reindex(index=C.index,columns=cs)
    Ebull=E[[sb.loc[d,s]>0.1 if pd.notna(sb.loc[d,s]) else False for d,s in zip(E.date,E.sym)]]
    Ebear=E[[sb.loc[d,s]<-0.1 if pd.notna(sb.loc[d,s]) else False for d,s in zip(E.date,E.sym)]]
    for lab,EE in [("all",E),("bullish",Ebull),("bearish",Ebear)]:
        for h in [1,5,20]:
            for sign,dir_ in [(1,"long (momentum)")]:
                r=calendar_time(EE,h,sign=sign,cost=0.003,split="2023-07-01",px_df=px_)
                if not r: continue
                out.append(dict(family="C_Social",hyp=f"WSB comment spike >={k}x 20d avg & >={minc}/day, {lab}, hold {h}d {dir_}",kind="eq",n=r["n"],effect=r["car_mean"],unit="% CAR net 30bp vs SPY",
                  t=r["t"],p=r["p"],eff_is=r["car_is"],t_is=r["t_is"],eff_oos=r["car_oos"],t_oos=r["t_oos"],p_oos=r["p_oos"],hit=r["hit"],n_oos=r["n_oos"],ct_ann=r["ann_ct"],start="2021-04",split="2023-07-01",source="Bradley et al. 2024 (RFS); Hu, Jones et al. 2021"))
                print(out[-1]["hyp"],r["n"],round(r["car_mean"],2),round(r["t"],2),"IS",round(r["car_is"],2),round(r["t_is"],2),"OOS",round(r["car_oos"],2),round(r["t_oos"],2),flush=True)
pd.DataFrame(out).to_csv("results/wsb.csv",index=False)
