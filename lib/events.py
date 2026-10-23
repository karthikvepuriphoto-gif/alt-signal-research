import numpy as np, pandas as pd
from common import nw
_PX=None
def px():
    global _PX
    if _PX is None:
        a=pd.read_parquet("data/eq_adj.parquet"); s=pd.read_csv("data/prices.csv",index_col=0,parse_dates=True)
        a["SPY"]=s["SPY"].reindex(a.index); _PX=a
    return _PX
def calendar_time(events, h, sign=1, cost=0.002, split="2019-01-01", lag=1, px_df=None, bench="SPY"):
    """events: DataFrame[sym,date]. Enter at close of `lag`-th trading day after date, hold h days.
    Returns dict with event-level CAR stats and calendar-time portfolio daily AR series."""
    P=px() if px_df is None else px_df
    R=P.pct_change(fill_method=None); AR=R.sub(R[bench],axis=0)
    idx=P.index; cars=[]; w=pd.DataFrame(0.0,index=idx,columns=P.columns)
    for sym,d in zip(events.sym,events.date):
        if sym not in P.columns: continue
        k=idx.searchsorted(pd.Timestamp(d),side="right")+lag-1   # first trading day strictly after d, + lag-1
        if k+h>=len(idx) or k<0: continue
        if pd.isna(P[sym].iloc[k]) or pd.isna(P[sym].iloc[k+h]): continue
        car=AR[sym].iloc[k+1:k+h+1].sum()
        cars.append((sym,idx[k],car)); w.iloc[k+1:k+h+1,w.columns.get_loc(sym)]+=1
    C=pd.DataFrame(cars,columns=["sym","entry","car"])
    if len(C)==0: return None
    n_act=w.sum(1); port=(w*AR.fillna(0)).sum(1)/n_act.replace(0,np.nan)
    port=port.dropna()*sign
    # costs: per-event round trip spread over its holding days, approximate
    port=port-cost/h
    C["car_net"]=sign*C.car-cost
    sp=pd.Timestamp(split); IS=C[C.entry<sp]; OS=C[C.entry>=sp]
    def st(x): 
        b,t,p,n=nw(x); return b,t,p,n
    full=st(port); i=st(port[port.index<sp]); o=st(port[port.index>=sp])
    return dict(n=len(C),n_is=len(IS),n_oos=len(OS),car_mean=C.car_net.mean()*100,car_is=IS.car_net.mean()*100 if len(IS) else np.nan,
        car_oos=OS.car_net.mean()*100 if len(OS) else np.nan, hit=(C.car_net>0).mean(),
        ct_bp=full[0]*1e4,t=full[1],p=full[2],t_is=i[1],t_oos=o[1],p_oos=o[2],ct_bp_is=i[0]*1e4,ct_bp_oos=o[0]*1e4,
        ann_ct=full[0]*252*100,port=port,C=C)
