import sys,json,glob,re; sys.path.insert(0,"lib")
from common import *; from events import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf
T=[]
for f in glob.glob("data/condensed_*.json"): T+=json.load(open(f))
t=pd.DataFrame(T).drop_duplicates("id_str"); t=t[~t.is_retweet.astype(bool)]
t["ts"]=pd.to_datetime(t.created_at,format="%a %b %d %H:%M:%S %z %Y").dt.tz_convert("America/New_York")
t=t[t.ts>="2016-11-09"]
M={"amazon":"AMZN","@amazon":"AMZN","boeing":"BA","lockheed":"LMT","general motors":"GM","ford":"F","toyota":"TM","carrier":"CARR_UTX","united technologies":"UTX","nordstrom":"JWN",
   "harley":"HOG","macy":"M","merck":"MRK","pfizer":"PFE","at&t":"T","comcast":"CMCSA","apple":"AAPL","google":"GOOGL","facebook":"META","twitter":"TWTR","new york times":"NYT","@nytimes":"NYT",
   "fiat":"FCAU","chrysler":"FCAU","walmart":"WMT","intel":"INTC","exxon":"XOM","soft bank":"SFTBY","softbank":"SFTBY","l.l.bean":None,"foxconn":None,"ibm":"IBM","dow chemical":"DOW_old","nike":"NKE",
   "u.s. steel":"X","us steel":"X","nbc":"CMCSA","cnn":"TWX","time warner":"TWX","washington post":"AMZN","@washingtonpost":"AMZN","goodyear":"GT","mattel":"MAT","sprint":"S","exxonmobil":"XOM","bayer":None,"novartis":"NVS","alcoa":None}
an=SentimentIntensityAnalyzer(); ev=[]
for _,r in t.iterrows():
    low=r.text.lower()
    for k,v in M.items():
        if v and re.search(r"(?<![a-z])"+re.escape(k)+r"(?![a-z])",low):
            ev.append(dict(sym=v,ts=r.ts,text=r.text[:140],sent=an.polarity_scores(r.text)["compound"]))
ev=pd.DataFrame(ev).drop_duplicates(["sym","ts"])
ev=ev[~ev.sym.isin(["CNN"])]
syms=sorted(set(ev.sym)-{"CARR_UTX","DOW_old"}); px_=yf.download(syms+["SPY","TWX"],start="2016-06-01",end="2019-12-31",auto_adjust=True,progress=False)["Close"]
ev.loc[ev.sym=="CARR_UTX","sym"]="UTX"
# event day: tweet after 16:00 or weekend -> next trading day is reaction day; enter at close of reaction day
ev["d"]=ev.ts.dt.tz_localize(None)
ev["date"]=np.where(ev.ts.dt.hour>=16,ev.d.dt.normalize(),ev.d.dt.normalize()-pd.Timedelta(days=1))
ev.to_csv("results/trump_company_tweets.csv",index=False)
print("company-mention tweets",len(ev),ev.sym.value_counts().head(10).to_dict())
rows=[]
R=px_.pct_change(fill_method=None); AR=R.sub(R.SPY,axis=0); idx=px_.index
d0=[]
for _,e in ev.iterrows():
    if e.sym not in AR: continue
    k=idx.searchsorted(pd.Timestamp(e.date),side="right")
    if k+6<len(idx): d0.append(dict(sym=e.sym,sent=e.sent,ar0=AR[e.sym].iloc[k],car1_5=AR[e.sym].iloc[k+1:k+6].sum()))
d0=pd.DataFrame(d0).dropna(); neg=d0[d0.sent<-0.05]; pos=d0[d0.sent>0.05]
for lab,g in [("negative",neg),("positive",pos)]:
    for col,desc in [("ar0","reaction day AR (NOT tradeable: tweet-time to close)"),("car1_5","CAR days +1..+5 after reaction-day close (tradeable)")]:
        b,tt,p,n=nw(g[col]-(0.002 if col=="car1_5" else 0)*(1 if lab=="positive" else -1),lags=0)
        rows.append(dict(family="C_Social",hyp=f"Trump {lab}-sentiment company tweet: {desc}",kind="eq",n=n,effect=g[col].mean()*100,t=nw(g[col],lags=0)[1],p=nw(g[col],lags=0)[2],unit="% AR vs SPY",start="2016-11",split="n/a (2.6y sample)",boot_p=boot_p(g[col]),source="Ge, Kurov & Wolfe 2019; Born, Myers & Clark 2017"))
        print(rows[-1]["hyp"],n,round(g[col].mean()*100,3),round(rows[-1]["t"],2))
pd.DataFrame(rows).to_csv("results/trump.csv",index=False)
