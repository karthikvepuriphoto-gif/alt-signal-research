import sys; sys.path.insert(0,"lib")
from common import *; from events import *
d=pd.read_csv("data/congress_house_ptr_rows.csv"); d["filed"]=pd.to_datetime(d.filed,errors="coerce"); d=d.dropna(subset=["filed","ticker"])
d["sym"]=d.ticker.str.upper().str.replace(".","-",regex=False); d=d[d.filed>="2019-01-01"]
P=px(); print("rows w/ ticker",len(d),"in universe",d.sym.isin(P.columns).sum())
rows=[]
def add(hyp,r):
    if not r: return
    rows.append(dict(family="B_Congress",hyp=hyp,kind="eq",n=r["n"],effect=r["car_mean"],unit="% CAR net vs SPY",t=r["t"],p=r["p"],eff_is=r["car_is"],t_is=r["t_is"],
        eff_oos=r["car_oos"],t_oos=r["t_oos"],p_oos=r["p_oos"],hit=r["hit"],n_oos=r["n_oos"],ct_ann=r["ann_ct"],split="2023-01-01",source="Ziobrowski et al. 2004/2011; Eggers & Hainmueller 2013; Belmont et al. 2022"))
    print(hyp,r["n"],"CAR",round(r["car_mean"],2),"t",round(r["t"],2),"IS",round(r["car_is"],2),round(r["t_is"],2),"OOS",round(r["car_oos"],2),round(r["t_oos"],2),flush=True)
buys=d[d.type=="P"].drop_duplicates(["sym","filed"]); big=d[(d.type=="P")&(d.lo>=50001)].drop_duplicates(["sym","filed"])
sells=d[d.type.str.startswith("S")].drop_duplicates(["sym","filed"])
for h in [21,63]:
    add(f"House member purchase, enter 2 trading days after filing, hold {h}d",calendar_time(buys[["sym"]].assign(date=buys.filed),h,lag=2,split="2023-01-01"))
    add(f"House member purchase >=$50k, hold {h}d",calendar_time(big[["sym"]].assign(date=big.filed),h,lag=2,split="2023-01-01"))
    add(f"House member sale -> short, hold {h}d",calendar_time(sells[["sym"]].assign(date=sells.filed),h,sign=-1,lag=2,split="2023-01-01"))
pd.DataFrame(rows).to_csv("results/congress.csv",index=False)
