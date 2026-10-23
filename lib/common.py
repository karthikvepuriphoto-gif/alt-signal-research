import numpy as np, pandas as pd, statsmodels.api as sm, warnings
warnings.filterwarnings("ignore")
D="data/"
def ff_monthly(path=D+"49_Industry_Portfolios.csv"):
    lines=open(path).read().splitlines()
    start=[i for i,l in enumerate(lines) if "Average Value Weighted Returns -- Monthly" in l][0]
    hdr=lines[start+1].split(","); rows=[]
    for l in lines[start+2:]:
        p=l.split(",")
        if len(p)<2 or not p[0].strip().isdigit() or len(p[0].strip())!=6: break
        rows.append(p)
    df=pd.DataFrame(rows,columns=[h.strip() for h in hdr]).set_index("")
    df.index=pd.to_datetime(df.index.str.strip(),format="%Y%m")+pd.offsets.MonthEnd(0)
    df=df.astype(float).replace([-99.99,-999],np.nan)/100
    return df
def ff_factors():
    lines=open(D+"F-F_Research_Data_Factors.csv").read().splitlines()
    i=[k for k,l in enumerate(lines) if l.startswith(",Mkt-RF")][0]; rows=[]
    for l in lines[i+1:]:
        p=l.split(",")
        if not p[0].strip().isdigit() or len(p[0].strip())!=6: break
        rows.append(p)
    df=pd.DataFrame(rows,columns=["d","MktRF","SMB","HML","RF"]).set_index("d")
    df.index=pd.to_datetime(df.index.str.strip(),format="%Y%m")+pd.offsets.MonthEnd(0)
    df=df.astype(float)/100; df["Mkt"]=df.MktRF+df.RF; return df
def ff_daily_factors():
    lines=open(D+"F-F_Research_Data_Factors_daily.csv").read().splitlines()
    i=[k for k,l in enumerate(lines) if l.startswith(",Mkt-RF")][0]; rows=[]
    for l in lines[i+1:]:
        p=l.split(",")
        if not p[0].strip().isdigit(): break
        rows.append(p)
    df=pd.DataFrame(rows,columns=["d","MktRF","SMB","HML","RF"]).set_index("d")
    df.index=pd.to_datetime(df.index.str.strip(),format="%Y%m%d")
    df=df.astype(float)/100; df["Mkt"]=df.MktRF+df.RF; return df
def prices():
    p=pd.read_csv(D+"prices.csv",index_col=0,parse_dates=True); return p
def nw(y,X=None,lags=None):
    y=pd.Series(y).dropna()
    if len(y)<8: return np.nan,np.nan,np.nan,len(y)
    if X is None: Xc=np.ones((len(y),1))
    else: Xc=sm.add_constant(pd.DataFrame(X).loc[y.index]).values
    lags=lags if lags is not None else int(4*(len(y)/100)**(2/9))
    r=sm.OLS(y.values,Xc).fit(cov_type="HAC",cov_kwds={"maxlags":lags})
    k=-1 if X is not None else 0
    return r.params[k],r.tvalues[k],r.pvalues[k],len(y)
def diff_test(a,b,lags=None):
    """mean(a)-mean(b) via regression on dummy, HAC."""
    a=pd.Series(a).dropna(); b=pd.Series(b).dropna()
    y=pd.concat([a,b]); d=pd.Series([1]*len(a)+[0]*len(b),index=y.index)
    y=y.reset_index(drop=True); d=d.reset_index(drop=True)
    if len(a)<5 or len(b)<5: return np.nan,np.nan,np.nan,len(a)
    r=sm.OLS(y.values,sm.add_constant(d.values)).fit(cov_type="HC1")
    return r.params[1],r.tvalues[1],r.pvalues[1],len(a)
def boot_p(x,n=5000,seed=0):
    x=np.asarray(pd.Series(x).dropna()); 
    if len(x)<5: return np.nan
    rng=np.random.default_rng(seed); m=x.mean(); xc=x-m
    bs=np.array([rng.choice(xc,len(x)).mean() for _ in range(n)])
    return (np.abs(bs)>=abs(m)).mean()
def sharpe(r,ppy=12):
    r=pd.Series(r).dropna(); return r.mean()/r.std()*np.sqrt(ppy) if r.std()>0 else np.nan
def bh(p):
    p=np.asarray(p,float); n=np.sum(~np.isnan(p)); q=np.full_like(p,np.nan)
    idx=np.where(~np.isnan(p))[0]; o=idx[np.argsort(p[idx])]
    ranks=np.arange(1,n+1); qq=p[o]*n/ranks; qq=np.minimum.accumulate(qq[::-1])[::-1]
    q[o]=np.minimum(qq,1); return q
