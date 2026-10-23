import sys; sys.path.insert(0,"lib")
from common import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fd=ff_daily_factors(); r=fd.MktRF.copy()            # CRSP value-weighted excess return, 1926-07 .. 2026-08
P=prices(); spy=P["SPY"].pct_change(); iwm=P["IWM"].pct_change()
idx=r.index; s=pd.Series(idx,index=idx)
# turn of month: last trading day + first 3
ym=idx.to_period("M"); g=pd.Series(1,index=idx).groupby(ym)
pos_f=g.cumcount().values; pos_b=(g.cumcount(ascending=False)).values
tom=(pos_f<=2)|(pos_b==0)
# pre-holiday: next trading day > 1 business day ahead (excludes normal weekends)
nxt=s.shift(-1); bd=np.array([np.busday_count(a.date(),b.date()) if pd.notna(b) else 1 for a,b in zip(s,nxt)])
preh=bd>1
# options expiration week: week (Mon-Fri) containing 3rd Friday
def third_fri(y,m):
    d=pd.Timestamp(y,m,1); return d+pd.Timedelta(days=(4-d.weekday())%7+14)
tf=pd.Series([third_fri(d.year,d.month) for d in idx],index=idx)
opex=((tf-pd.to_timedelta(4,"D"))<=idx)&(idx<=tf)
# FOMC announcement day
fomc=pd.to_datetime(pd.read_csv("data/fomc_dates.csv").iloc[:,0]); isf=idx.isin(fomc)
# moon: phase age in days
ref=pd.Timestamp("2000-01-06 18:14"); age=((idx+pd.Timedelta(hours=16)-ref)/pd.Timedelta(days=1))%29.530589
newm=(age<=3)|(age>=29.53-3); fullm=np.abs(age-14.765)<=3
# DST Mondays
def dst_dates(y):
    if y<1967: return []
    if y in (1974,1975): return []
    def nth_sun(y,m,n,last=False):
        if last:
            d=pd.Timestamp(y,m,1)+pd.offsets.MonthEnd(0); return d-pd.Timedelta(days=(d.weekday()+1)%7)
        d=pd.Timestamp(y,m,1); return d+pd.Timedelta(days=(6-d.weekday())%7+7*(n-1))
    if y<=1986: return [nth_sun(y,4,0,True),nth_sun(y,10,0,True)]
    if y<=2006: return [nth_sun(y,4,1),nth_sun(y,10,0,True)]
    return [nth_sun(y,3,2),nth_sun(y,11,1)]
dsts=[d for y in range(1967,2027) for d in dst_dates(y)]
first_after=[idx[idx>d][0] for d in dsts if (idx>d).any()]
isdst=idx.isin(first_after); mon=idx.weekday==0
H=[("Pre-FOMC/FOMC announcement day",pd.Series(isf,index=idx),"1994-01-01","2011-01-01","Lucca & Moench (2015; SSRN 2011)"),
   ("Turn-of-month (day -1..+3)",pd.Series(tom,index=idx),"1926-07-01","1988-01-01","Ariel 1987; Lakonishok & Smidt 1988"),
   ("Pre-holiday day",pd.Series(preh,index=idx),"1926-07-01","1990-01-01","Ariel 1990"),
   ("Options-expiration week",pd.Series(opex,index=idx),"1973-05-01","2005-01-01","Ni, Pearson & Poteshman 2005"),
   ("New-moon +/-3d vs full-moon +/-3d (null check)",pd.Series(newm,index=idx),"1926-07-01","2006-01-01","Yuan, Zheng & Zhu 2006; Dichev & Janes 2003"),
   ("Monday after DST change vs other Mondays",pd.Series(isdst,index=idx),"1967-01-01","2000-01-01","Kamstra, Kramer & Levi 2000"),
   ("Monday vs other weekdays",pd.Series(mon,index=idx),"1926-07-01","1980-01-01","French 1980")]
rows=[]
def run(name,mask,start,pub,src,series,sname,cost):
    x=series.dropna(); x=x[x.index>=start]; m=mask.reindex(x.index).fillna(False).astype(bool)
    base=~m
    if name.startswith("New-moon"): base=pd.Series(fullm,index=idx).reindex(x.index).fillna(False).astype(bool)
    if name.startswith("Monday after DST"): base=pd.Series(mon&~isdst,index=idx).reindex(x.index).fillna(False).astype(bool)
    d=diff_test(x[m],x[base]); IS=x.index<pub
    di=diff_test(x[m&IS],x[base&IS]); do=diff_test(x[m&~IS],x[base&~IS])
    # OOS strategy: long market only on event days (if IS effect>0), cost per entry+exit
    pos=m[~IS].astype(float)*np.sign(di[0]); entries=(pos.diff().abs()>0).sum()/2
    yrs=(~IS).sum()/252
    strat_ann=(pos*x[~IS]).sum()/yrs - entries*cost/yrs
    rows.append(dict(family="B_Calendar",hyp=f"{name} [{sname}]",kind="eq",n=int(m.sum()),start=str(x.index[0].date()),split=pub,effect=d[0]*1e4,t=d[1],p=d[2],
        eff_is=di[0]*1e4,t_is=di[1],eff_oos=do[0]*1e4,t_oos=do[1],p_oos=do[2],unit="bp/day diff",source=src,
        oos_strat_ann=strat_ann*100,oos_exposure=float(m[~IS].mean())))
for name,mask,start,pub,src in H:
    run(name,mask,start,pub,src,r,"CRSP VW mkt excess",0.0002)
    run(name,mask,max(start,"1993-02-01"),max(pub,"2005-01-01") if pub<"1993-02-01" else pub,src,spy,"SPY",0.0002)
    run(name,mask,max(start,"2000-06-01"),max(pub,"2013-01-01") if pub<"2000-06-01" else pub,src,iwm,"IWM small caps",0.0003)
# Halloween monthly
fac=ff_factors(); m=fac.MktRF; hw=pd.Series(m.index.month.isin([11,12,1,2,3,4]),index=m.index)
d=diff_test(m[hw],m[~hw]); IS=m.index<"2002-01-01"; di=diff_test(m[hw&IS],m[~hw&IS]); do=diff_test(m[hw&~IS],m[~hw&~IS])
rows.append(dict(family="B_Calendar",hyp="Halloween (Nov-Apr vs May-Oct) [CRSP monthly]",kind="eq",n=int(hw.sum()),start="1926-07-01",split="2002-01-01",effect=d[0]*100,t=d[1],p=d[2],eff_is=di[0]*100,t_is=di[1],eff_oos=do[0]*100,t_oos=do[1],p_oos=do[2],unit="%/month diff",source="Bouman & Jacobsen 2002"))
res=pd.DataFrame(rows); res.to_csv("results/calendar.csv",index=False)
print(res[["hyp","n","effect","t","p","eff_is","t_is","eff_oos","t_oos","oos_strat_ann","oos_exposure"]].to_string())
# rolling chart TOM and FOMC
fig,ax=plt.subplots(2,1,figsize=(10,6))
for a,(nm,mk) in zip(ax,[("Turn-of-month",tom),("FOMC day",isf)]):
    mk=pd.Series(mk,index=idx); y=(r[mk]).groupby(r[mk].index.year).mean()*1e4-(r[~mk]).groupby(r[~mk].index.year).mean()*1e4
    y.rolling(5,min_periods=3).mean().plot(ax=a); a.axhline(0,color="k"); a.set_title(nm+": event-day minus other-day mean (bp), 5y rolling")
fig.tight_layout(); fig.savefig("charts/calendar_rolling.png",dpi=110)
