import sys,glob,os; sys.path.insert(0,"lib")
from common import *; from events import *
P=px(); rows=[]
def add(fam,hyp,r,src,unit="% CAR net vs SPY"):
    if not r: return
    rows.append(dict(family=fam,hyp=hyp,kind="eq",n=r["n"],effect=r["car_mean"],unit=unit,t=r["t"],p=r["p"],eff_is=r["car_is"],t_is=r["t_is"],
        eff_oos=r["car_oos"],t_oos=r["t_oos"],p_oos=r["p_oos"],hit=r["hit"],n_oos=r["n_oos"],ct_ann=r["ann_ct"],split="2019-01-01",source=src))
    print(hyp,r["n"],"CAR",round(r["car_mean"],2),"t",round(r["t"],2),"IS",round(r["car_is"],2),round(r["t_is"],2),"OOS",round(r["car_oos"],2),round(r["t_oos"],2),flush=True)
# ---- PEAD
E=[]
for f in glob.glob("data/earn/*.csv"):
    if os.path.getsize(f)==0: continue
    e=pd.read_csv(f); 
    if "Surprise(%)" not in e: continue
    e=e.dropna(subset=["Surprise(%)"]); e["sym"]=os.path.basename(f)[:-4]; E.append(e)
E=pd.concat(E); E["ts"]=pd.to_datetime(E["Earnings Date"],utc=True).dt.tz_convert("America/New_York")
E["d"]=E.ts.dt.tz_localize(None).dt.normalize(); pre=E.ts.dt.hour<12
E["date"]=E.d-pd.to_timedelta(pre.astype(int),"D")    # pre-market: reaction same day -> treat as prior day
E=E[E.d>="2006-01-01"].sort_values("d"); s=E["Surprise(%)"].clip(-200,200)
# trailing 365-day percentile thresholds (no lookahead)
E=E.set_index("d"); q90=s.set_axis(E.index).rolling("365D").quantile(0.9).shift(1); q10=s.set_axis(E.index).rolling("365D").quantile(0.1).shift(1)
E["q90"]=q90.values; E["q10"]=q10.values; E=E.reset_index(); E=E[E.d>="2007-01-01"]
top=E[E["Surprise(%)"]>=E.q90][["sym","date"]]; bot=E[E["Surprise(%)"]<=E.q10][["sym","date"]]
print("earnings events",len(E),"top",len(top),"bot",len(bot))
for h in [21,63]:
    add("B_PEAD",f"PEAD long top-decile EPS surprise, enter close day after reaction, hold {h}d",calendar_time(top,h,lag=2),"Bernard & Thomas 1989")
    add("B_PEAD",f"PEAD short bottom-decile EPS surprise, hold {h}d",calendar_time(bot,h,sign=-1,lag=2),"Bernard & Thomas 1989")
# ---- index additions (S&P 500)
w=pd.read_csv("data/wiki_changes.csv"); w["eff"]=pd.to_datetime(w.date,errors="coerce"); w=w.dropna(subset=["eff"])
adds=pd.DataFrame({"sym":w.add_t.str.strip(),"date":w.eff-pd.Timedelta(days=1)}).dropna()
rems=pd.DataFrame({"sym":w.rem_t.str.strip(),"date":w.eff-pd.Timedelta(days=1)}).dropna()
print("adds",len(adds),"removals",len(rems), "removals with prices", rems.sym.isin(P.columns).sum())
for h in [5,21,63]:
    add("B_Index",f"S&P500 addition: short from close of effective day, hold {h}d (post-inclusion reversal)",calendar_time(adds,h,sign=-1),"Shleifer 1986; Harris & Gurel 1986; Greenwood & Sammon 2022")
    add("B_Index",f"S&P500 deletion: long from close of effective day, hold {h}d (rebound)",calendar_time(rems,h),"Chen, Noronha & Singal 2004")
pd.DataFrame(rows).to_csv("results/events_b.csv",index=False)
