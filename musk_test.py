import sys; sys.path.insert(0,"lib")
from common import *
P=prices(); dg=P["DOGE-USD"].dropna(); bt=P["BTC-USD"].reindex(dg.index)
R=dg.pct_change(); RB=bt.pct_change(); AR=R-RB
m=pd.read_csv("data/musk/musk_doge_posts.csv"); m["d"]=pd.to_datetime(m.created_at).dt.tz_convert("UTC").dt.tz_localize(None).dt.normalize()
days=sorted(set(m.d)); idx=dg.index; out=[]
for d in days:
    if d not in idx: continue
    k=idx.get_loc(d)
    if k+5>=len(idx): continue
    out.append(dict(d=d,ar0=AR.iloc[k],r0=R.iloc[k],car1=AR.iloc[k+1],car5=AR.iloc[k+1:k+6].sum(),r5=R.iloc[k+1:k+6].sum()))
o=pd.DataFrame(out).dropna(); rows=[]
for col,desc,tr in [("ar0","tweet-day DOGE-BTC AR (NOT tradeable)",0),("car1","next-day AR after tweet-day close",1),("car5","AR days +1..+5 after tweet-day close",1)]:
    x=o[col]-0.002*tr; b,t,p,n=nw(x,lags=0)
    rows.append(dict(family="C_Social",hyp=f"Musk Dogecoin post: {desc}",kind="crypto",n=n,effect=x.mean()*100,t=t,p=p,boot_p=boot_p(x),unit="% (net 20bp if tradeable)",start="2019-04",split="n/a; 58 of 90 posts in 2021",source="Ante 2023 (Tech. Forecasting & Soc. Change)"))
    print(rows[-1]["hyp"],n,round(x.mean()*100,2),round(t,2),round(rows[-1]["boot_p"],3))
pre=o[o.d<"2021-06-01"]; post=o[o.d>="2021-06-01"]
print("ar0 pre-Jun2021",len(pre),round(pre.ar0.mean()*100,2)," post",len(post),round(post.ar0.mean()*100,2))
pd.DataFrame(rows).to_csv("results/musk.csv",index=False); o.to_csv("results/musk_doge_events.csv",index=False)
