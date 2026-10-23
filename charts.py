import sys; sys.path.insert(0,"lib")
from common import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
A=pd.read_csv("results/ALL_HYPOTHESES_ranked.csv")
top=A.head(30).iloc[::-1]
fig,ax=plt.subplots(figsize=(11,9)); c=["tab:green" if s and o else ("tab:orange" if s else "tab:gray") for s,o in zip(top.survives_BH,top.oos_confirms)]
ax.barh(range(len(top)),top.t.abs(),color=c); ax.set_yticks(range(len(top))); ax.set_yticklabels(top.hyp.str.slice(0,75),fontsize=7)
ax.set_xlabel("|t-stat| full sample"); ax.set_title(f"Top 30 of {len(A)} hypotheses\ngreen = survives BH (q<5%) + OOS confirms; orange = BH only; gray = neither",fontsize=10)
fig.tight_layout(); fig.savefig("charts/all_hypotheses_top30.png",dpi=110)
# p-value histogram
fig,ax=plt.subplots(figsize=(7,4)); ax.hist(A.p.dropna(),bins=20,edgecolor="k"); ax.axhline(len(A)/20,color="r",ls="--",label="expected if all null"); ax.legend(); ax.set_xlabel("p-value"); ax.set_title("p-value distribution, all hypotheses")
fig.tight_layout(); fig.savefig("charts/pvalue_histogram.png",dpi=110)

src=open("enso_backtest.py").read().split("rows=[]")[0].replace("LAG=int(sys.argv[1]) if len(sys.argv)>1 else 2","LAG=1").replace("THR=float(sys.argv[2]) if len(sys.argv)>2 else 0.5","THR=0.5")
H=A; exec(src); ASSETS=A; A=H
fig,axs=plt.subplots(1,3,figsize=(15,4))
for ax,(nm,reg) in zip(axs,[("Fert CF+MOS-SPY","ElNino"),("Fut ZW=F","ElNino"),("PPI crude","LaNina")]):
    r=ASSETS[nm][0].dropna(); s=pd.Series(oni.reindex(r.index-pd.offsets.MonthEnd(1)).values,index=r.index)
    m=(s>=0.5) if reg=="ElNino" else (s<=-0.5)
    ax.plot(r.where(m,0).cumsum(),label=f"in {reg} months"); ax.plot(r.where(~m,0).cumsum(),label="other months"); ax.set_title(nm+" cumulative (sum of monthly)"); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig("charts/enso_regime_cumulative.png",dpi=110)
for f,t in [("results/insider_cluster3_21d_ct.csv","Insider clusters (>=3) 21d, calendar-time cum AR")]:
    x=pd.read_csv(f,index_col=0,parse_dates=True).iloc[:,0]
    fig,ax=plt.subplots(figsize=(8,3.5)); x.plot(ax=ax); ax.set_title(t); fig.tight_layout(); fig.savefig("charts/insider_cluster3_cum.png",dpi=110)
m=pd.read_csv("results/musk_doge_events.csv")
fig,ax=plt.subplots(figsize=(7,4)); ax.bar(["tweet day","day +1","days +1..+5"],[m.ar0.mean()*100,m.car1.mean()*100,m.car5.mean()*100]); ax.set_ylabel("% DOGE minus BTC"); ax.set_title(f"Musk Dogecoin posts (n={len(m)} days)"); fig.tight_layout(); fig.savefig("charts/musk_doge.png",dpi=110)
