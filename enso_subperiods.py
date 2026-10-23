import sys; sys.path.insert(0,"lib")
from common import *
import statsmodels.api as sm
exec(open("enso_backtest.py").read().split("rows=[]")[0].replace("LAG=int(sys.argv[1]) if len(sys.argv)>1 else 2","LAG=1").replace("THR=float(sys.argv[2]) if len(sys.argv)>2 else 0.5","THR=0.5"))
keys=[("IMF wheat","ElNino"),("Fut ZW=F","ElNino"),("Fert CF+MOS-SPY","ElNino"),("ETF EWW-SPY","ElNino"),("FF:Coal-Mkt","LaNina"),("PPI crude","LaNina"),("Fut CL=F","LaNina"),("IMF maize","LaNina"),("Fut ZC=F","LaNina"),("PPI wheat","ElNino")]
out=[]
for name,reg in keys:
    r,kind=A[name]; r=r.dropna(); r=r[r.index>="1950-01-01"]
    s=pd.Series(oni.reindex(r.index-pd.offsets.MonthEnd(1)).values,index=r.index)
    df=pd.DataFrame({"r":r,"s":s}).dropna(); df["mask"]=(df.s>=0.5) if reg=="ElNino" else (df.s<=-0.5)
    df["mom12"]=df.r.rolling(12).sum().shift(1); df["rev1"]=df.r.shift(1)
    row={"series":name,"regime":reg}
    for a,b in [(1950,1975),(1975,2000),(2000,2013),(2013,2027)]:
        x=df[(df.index.year>=a)&(df.index.year<b)]
        if x["mask"].sum()>=6: d=diff_test(x.r[x["mask"]],x.r[~x["mask"]]); row[f"{a}-{b-1}"]=f"{d[0]*100:+.2f} (t={d[1]:.1f}, n={int(x['mask'].sum())})"
        else: row[f"{a}-{b-1}"]="n/a"
    x=df.dropna(); X=sm.add_constant(pd.DataFrame({"regime":x["mask"].astype(float),"mom12":x.mom12,"rev1":x.rev1}))
    f=sm.OLS(x.r,X).fit(cov_type="HAC",cov_kwds={"maxlags":6}); row["controlled for own 12m momentum & 1m reversal"]=f"{f.params['regime']*100:+.2f} (t={f.tvalues['regime']:.1f})"
    out.append(row)
o=pd.DataFrame(out); o.to_csv("results/enso_subperiods_controls.csv",index=False); print(o.to_string())
