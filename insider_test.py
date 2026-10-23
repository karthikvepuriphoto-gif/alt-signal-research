import sys; sys.path.insert(0,"lib")
from common import *; from events import *
d=pd.read_parquet("data/insider_purchases.parquet").dropna(subset=["FILING_DATE","TRANS_DATE"])
d=d[(d.value>=10000)&(d.TRANS_DATE>="2011-01-01")]
P=px(); d=d[d.sym.isin(P.columns)]
print("purchases in universe",len(d))
rows=[]
def clusters(k,win=30):
    ev=[]
    for sym,g in d.sort_values("FILING_DATE").groupby("sym"):
        g=g.drop_duplicates(["RPTOWNERCIK","FILING_DATE"]); last=pd.Timestamp("1900-01-01")
        fd=g.FILING_DATE.values; td=g.TRANS_DATE.values; ow=g.RPTOWNERCIK.values
        for i in range(len(g)):
            m=(td>=td[i]-np.timedelta64(win,"D"))&(td<=td[i])&(fd<=fd[i])
            if len(set(ow[m]))>=k and (fd[i]-np.datetime64(last))>np.timedelta64(90,"D"):
                ev.append((sym,pd.Timestamp(fd[i]))); last=pd.Timestamp(fd[i])
    return pd.DataFrame(ev,columns=["sym","date"])
for k in [1,2,3]:
    ev=clusters(k); 
    for h in [5,21,63]:
        r=calendar_time(ev,h)
        if r: rows.append(dict(family="B_Insider",hyp=f"Insider open-mkt buy cluster >={k} insiders/30d, hold {h}d (entry day after filing)",kind="eq",n=r["n"],
            effect=r["car_mean"],unit="% CAR net of 20bp vs SPY",t=r["t"],p=r["p"],eff_is=r["car_is"],t_is=r["t_is"],eff_oos=r["car_oos"],t_oos=r["t_oos"],p_oos=r["p_oos"],
            hit=r["hit"],n_oos=r["n_oos"],ct_ann=r["ann_ct"],start="2011",split="2019-01-01",source="Cohen, Malloy & Pomorski 2012; Lakonishok & Lee 2001"))
        if r: print(rows[-1]["hyp"],r["n"],round(r["car_mean"],2),round(r["t"],2),"IS",round(r["car_is"],2),round(r["t_is"],2),"OOS",round(r["car_oos"],2),round(r["t_oos"],2),flush=True)
        if k==3 and h==21: r["port"].cumsum().to_csv("results/insider_cluster3_21d_ct.csv")
pd.DataFrame(rows).to_csv("results/insider.csv",index=False)
