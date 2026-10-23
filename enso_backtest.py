import sys; sys.path.insert(0,"lib")
from common import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
LAG=int(sys.argv[1]) if len(sys.argv)>1 else 2   # months after season-end month before usable
THR=float(sys.argv[2]) if len(sys.argv)>2 else 0.5
tag=f"lag{LAG}_thr{THR}"
# ONI
o=pd.read_csv("oni.txt",sep=r"\s+")
cen={"DJF":1,"JFM":2,"FMA":3,"MAM":4,"AMJ":5,"MJJ":6,"JJA":7,"JAS":8,"ASO":9,"SON":10,"OND":11,"NDJ":12}
o["cm"]=[pd.Timestamp(int(y),cen[s],1) for s,y in zip(o.SEAS,o.YR)]
o.loc[o.SEAS=="DJF","cm"]=[pd.Timestamp(int(y),1,1) for y in o.loc[o.SEAS=="DJF","YR"]]
# season ends cm+1; usable at end of month cm+1+LAG
o["known"]=[ (c+pd.DateOffset(months=1+LAG))+pd.offsets.MonthEnd(0) for c in o.cm]
oni=o.set_index("known").ANOM.sort_index(); oni=oni[~oni.index.duplicated(keep="last")]
oni=oni.asfreq("ME").ffill()
# assets
ff=ff_monthly(); fac=ff_factors(); mkt=fac.Mkt; rf=fac.RF
A={}
for c in ["Agric","Food","Chems","Insur","Util","Ships","Oil","Coal","Mines","BldMt","Cnstr","Rtail","Steel","Gold","Fin"]:
    A[f"FF:{c}-Mkt"]=(ff[c]-mkt,"eq")
A["FF:Mkt-RF"]=(fac.MktRF,"eq")
for s,n in [("WPU01220205","PPI corn"),("WPU0121","PPI wheat"),("WPU0561","PPI crude"),("WPU0221","PPI WPU0221")]:
    x=pd.read_csv(f"data/fred_{s}.csv",index_col=0,parse_dates=True).iloc[:,0]; x.index=x.index+pd.offsets.MonthEnd(0)
    A[n]=(pd.to_numeric(x,errors="coerce").pct_change(),"cmdNI")
for s,n in [("PCOFFOTMUSDM","IMF coffee"),("PMAIZMTUSDM","IMF maize"),("PWHEAMTUSDM","IMF wheat"),("PSUGAISAUSDM","IMF sugar"),("PNGASUSUSDM","IMF US natgas")]:
    x=pd.read_csv(f"data/fred_{s}.csv",index_col=0,parse_dates=True).iloc[:,0]; x.index=x.index+pd.offsets.MonthEnd(0)
    A[n]=(pd.to_numeric(x,errors="coerce").pct_change(),"cmdNI")
P=prices().resample("ME").last(); R=P.pct_change(fill_method=None); R=R.mask(R.abs()>1.5)  # drop data glitches (e.g. NVR 1993)
spx=R["^GSPC"]
for t in ["ZC=F","ZW=F","KC=F","NG=F","SB=F","CL=F","ZS=F","CC=F"]: A["Fut "+t]=(R[t],"cmd")
for t in ["^AXJO","^BVSP","^BSESN"]: A["Idx "+t+"-SPX(local ccy)"]=(R[t]-spx,"eq")
for t in ["EWA","EWZ","EPU","EWM","EIDO","ECH","INDA","EWW"]: A["ETF "+t+"-SPY"]=(R[t]-R["SPY"],"eq")
A["Fert CF+MOS-SPY"]=(R[["CF","MOS"]].mean(1,skipna=True)-R["SPY"],"eq")
A["Reins RNR+EG+ACGL-SPY"]=(R[["RNR","EG","ACGL"]].mean(1)-R["SPY"],"eq")
rows=[]
for name,(r,kind) in A.items():
    r=r.dropna(); r=r[r.index>="1950-01-01"]
    sig=oni.reindex(r.index-pd.offsets.MonthEnd(1)).values  # signal known at end of prior month
    df=pd.DataFrame({"r":r.values,"s":sig},index=r.index).dropna()
    if len(df)<60: continue
    df["r3"]=df.r.rolling(3).sum().shift(-2)
    split=pd.Timestamp("2000-01-01") if df.index[0]<pd.Timestamp("1985-01-01") else df.index[len(df)//2]
    IS,OS=df[df.index<split],df[df.index>=split]
    for h,col,lg in [(1,"r",None),(3,"r3",3)]:
        b,t,p,n=nw(df[col],df.s,lg); bi,ti,pi,ni=nw(IS[col],IS.s,lg); bo,to,po,no=nw(OS[col],OS.s,lg)
        rows.append(dict(family="A_ENSO",hyp=f"{name} | next{h}m ret ~ ONI",kind=kind,n=n,start=str(df.index[0].date()),split=str(split.date()),
            effect=b*100,t=t,p=p,eff_is=bi*100,t_is=ti,eff_oos=bo*100,t_oos=to,p_oos=po,unit="%/month per 1C ONI"))
    for reg,mask in [("ElNino",df.s>=THR),("LaNina",df.s<=-THR)]:
        if h!=1: pass
        d=diff_test(df.r[mask],df.r[~mask]); di=diff_test(IS.r[mask.loc[IS.index]],IS.r[~mask.loc[IS.index]]); do=diff_test(OS.r[mask.loc[OS.index]],OS.r[~mask.loc[OS.index]])
        # OOS trade: hold asset in regime if IS diff>0 else short (for eq excess: long/short vs mkt); cost 10bp eq /20bp cmd per switch
        sgn=np.sign(di[0]) if not np.isnan(di[0]) else 0
        pos=(mask.loc[OS.index].astype(float)*sgn); cost=(0.002 if kind.startswith("cmd") else 0.001)*pos.diff().abs().fillna(abs(pos.iloc[0]))
        strat=pos*OS.r-cost
        rows.append(dict(family="A_ENSO",hyp=f"{name} | {reg}(ONI{'>=' if reg=='ElNino' else '<=-'}{THR}) vs other months",kind=kind,n=d[3],start=str(df.index[0].date()),split=str(split.date()),
            effect=d[0]*100,t=d[1],p=d[2],eff_is=di[0]*100,t_is=di[1],eff_oos=do[0]*100,t_oos=do[1],p_oos=do[2],unit="%/month diff",
            oos_strat_ann=strat.mean()*1200,oos_strat_t=nw(strat)[1],oos_months_in=int(mask.loc[OS.index].sum())))
res=pd.DataFrame(rows); res.to_csv(f"results/enso_{tag}.csv",index=False)
# hurricane season
H=[]
hs={"FF:Insur-Mkt":ff["Insur"]-mkt,"Reins RNR+EG+ACGL-SPY":R[["RNR","EG","ACGL"]].mean(1)-R["SPY"],"Prop ins ALL+TRV+PGR+CB-SPY":R[["ALL","TRV","PGR","CB"]].mean(1)-R["SPY"],
    "FF:Cnstr-Mkt":ff["Cnstr"]-mkt,"FF:BldMt-Mkt":ff["BldMt"]-mkt,"Homebuilders LEN+DHI+PHM+NVR-SPY":R[["LEN","DHI","PHM","NVR"]].mean(1)-R["SPY"],"HD+LOW-SPY":R[["HD","LOW"]].mean(1)-R["SPY"],
    "FF:Util-Mkt":ff["Util"]-mkt,"Fut NG=F":R["NG=F"]}
for name,r in hs.items():
    r=r.dropna(); r=r[r.index>="1950-01-01"]
    split=pd.Timestamp("2000-01-01") if r.index[0]<pd.Timestamp("1985-01-01") else r.index[len(r)//2]
    for lab,months in [("Aug-Oct peak",[8,9,10]),("Jun-Nov season",[6,7,8,9,10,11])]:
        m=r.index.month.isin(months); m=pd.Series(m,index=r.index)
        d=diff_test(r[m],r[~m]); IS=r.index<split
        di=diff_test(r[m&IS],r[~m&IS]); do=diff_test(r[m&~IS],r[~m&~IS])
        H.append(dict(family="A_Hurricane",hyp=f"{name} | {lab} vs rest",kind="eq",n=d[3],start=str(r.index[0].date()),split=str(split.date()),effect=d[0]*100,t=d[1],p=d[2],
            eff_is=di[0]*100,t_is=di[1],eff_oos=do[0]*100,t_oos=do[1],p_oos=do[2],unit="%/month diff"))
pd.DataFrame(H).to_csv(f"results/hurricane.csv",index=False)
if tag=="lag1_thr0.5":
    fig,ax=plt.subplots(figsize=(11,3.5)); ax.fill_between(oni.index,oni.values,0,where=oni.values>0,color="tab:red"); ax.fill_between(oni.index,oni.values,0,where=oni.values<0,color="tab:blue")
    ax.set_title("ONI as known in real time (usable at end of month after season end)"); fig.tight_layout(); fig.savefig("charts/oni_realtime.png",dpi=110)
    top=res[res.hyp.str.contains("ElNino|LaNina")].sort_values("p").head(12)
    fig,ax=plt.subplots(figsize=(10,6)); y=np.arange(len(top)); ax.barh(y-0.2,top.eff_is,0.4,label="in-sample"); ax.barh(y+0.2,top.eff_oos,0.4,label="out-of-sample")
    ax.set_yticks(y); ax.set_yticklabels(top.hyp.str.slice(0,60),fontsize=7); ax.axvline(0,color="k"); ax.legend(); ax.set_xlabel("%/month difference"); ax.set_title("Top ENSO regime effects: IS vs OOS"); fig.tight_layout(); fig.savefig("charts/enso_top_is_oos.png",dpi=110)
print(res.sort_values("p").head(25)[["hyp","n","effect","t","p","eff_is","eff_oos","t_oos"]].to_string())
print(pd.DataFrame(H).sort_values("p")[["hyp","effect","t","p","eff_is","eff_oos","t_oos"]].to_string())
