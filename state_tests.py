"""Phase 2 state-level signal tests. Implements PREREGISTRATION.md exactly; extras labelled exploratory."""
import sys, glob, re; sys.path.insert(0,"lib")
from common import *
from events import px, calendar_time
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
rows=[]; CASE=[]
def add(fam,hyp,pred,n,eff,unit,t,p,eis,tis,eoos,toos,poos,src,kind="",prereg=True,start=None,split=None):
    rows.append(dict(family=fam,hyp=hyp,pred_sign=pred,n=n,effect=eff,unit=unit,t=t,p=p,eff_is=eis,t_is=tis,eff_oos=eoos,t_oos=toos,p_oos=poos,
                     dir_ok=(np.sign(eff)==pred) if pd.notna(eff) else np.nan,source=src,kind=kind,prereg=prereg,start=start,split=split))
# ---------- prices
E=px(); X=pd.read_parquet("data/state/px_extra.parquet")
P=X.combine_first(E) if True else None
P=P.sort_index(); P=P[P.index>="2000-01-01"]
M=P.resample("ME").last().pct_change(fill_method=None); M=M.mask(M.abs()>1.5)
MX=M.sub(M["SPY"],axis=0)                 # monthly excess vs SPY
UNIV=[c for c in E.columns if c!="SPY"]
hq=pd.read_csv("data/state/hq_states.csv"); hq=hq[hq.hq_state.str.len()==2] if hq.hq_state.dtype==object else hq
US=set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())
hq=hq[hq.hq_state.isin(US)]; ST=hq.set_index("ticker").hq_state; SIC=hq.set_index("ticker").sic
print("HQ mapped",len(hq),"of",len(set(UNIV))," states:",ST.value_counts().head(8).to_dict())
def mreg(y,x,split,lags=6):
    d=pd.concat([y,x],axis=1).dropna(); d.columns=["y","x"]
    f=nw(d.y,d[["x"]],lags); i=nw(d.y[d.index<split],d[["x"]][d.index<split],lags); o=nw(d.y[d.index>=split],d[["x"]][d.index>=split],lags)
    return f,i,o,d
def regrow(fam,hyp,pred,y,x,split,src,unit="% next-month excess ret vs SPY per 1sd signal",scale=100,start=None):
    x=(x-x.mean())/x.std() if x.nunique()>2 else x
    f,i,o,d=mreg(y,x,split)
    add(fam,hyp,pred,f[3],f[0]*scale,unit,f[1],f[2],i[0]*scale,i[1],o[0]*scale,o[1],o[2],src,"monthly-reg",start=str(d.index.min().date()) if len(d) else None,split=split)
    return d
def lsrow(fam,hyp,pred,ls,split,src,unit="% per month L-S net of 10bp/side"):
    ls=ls.dropna(); f=nw(ls,None,6); i=nw(ls[ls.index<split],None,6); o=nw(ls[ls.index>=split],None,6)
    add(fam,hyp,pred,f[3],f[0]*100,unit,f[1],f[2],i[0]*100,i[1],o[0]*100,o[1],o[2],src,"monthly-LS",start=str(ls.index.min().date()),split=split)
def tercile_ls(sig_by_stock, high_long=True, seed=0):
    """sig_by_stock: DataFrame month x stock (known at end of month t). Long top tercile (if high_long) minus bottom, return t+1, net turnover cost."""
    rng=np.random.default_rng(seed); out={}; wprev=pd.Series(dtype=float)
    R=M
    for t in sig_by_stock.index:
        s=sig_by_stock.loc[t].dropna()
        nxt=t+pd.offsets.MonthEnd(1)
        if nxt not in R.index or len(s)<30: continue
        r=R.loc[nxt,s.index]; s=s[r.notna()]
        if len(s)<30: continue
        rk=(s+rng.normal(0,1e-9,len(s))).rank(pct=True)
        L=s.index[rk>2/3]; S=s.index[rk<=1/3]
        if not high_long: L,S=S,L
        w=pd.concat([pd.Series(1/len(L),L),pd.Series(-1/len(S),S)]).groupby(level=0).sum()
        to=w.sub(wprev,fill_value=0).abs().sum(); wprev=w
        out[nxt]=(R.loc[nxt,L].mean()-R.loc[nxt,S].mean())-0.001*to
    return pd.Series(out)
# ---------- ONI (lag 1)
o=pd.read_csv("oni.txt",sep=r"\s+"); cen={"DJF":1,"JFM":2,"FMA":3,"MAM":4,"AMJ":5,"MJJ":6,"JJA":7,"JAS":8,"ASO":9,"SON":10,"OND":11,"NDJ":12}
o["cm"]=[pd.Timestamp(int(y),cen[s],1) for s,y in zip(o.SEAS,o.YR)]
o["known"]=[(c+pd.DateOffset(months=2))+pd.offsets.MonthEnd(0) for c in o.cm]
oni=o.set_index("known").ANOM.sort_index(); oni=oni[~oni.index.duplicated(keep="last")].asfreq("ME").ffill()
# ---------- drought
dd={}
for f in glob.glob("data/state/usdm_*.csv"):
    d=pd.read_csv(f)
    if len(d)==0: continue
    st=d.StateAbbreviation.iloc[0]; tot=d[["None","D0","D1","D2","D3","D4"]].sum(1)
    d2=(d.D2+d.D3+d.D4) if tot.median()>99 else d.D2      # categorical vs cumulative
    d["rel"]=pd.to_datetime(d.MapDate.astype(str))+pd.Timedelta(days=2)    # released Thursday after Tuesday valid date
    dd[st]=pd.Series(d2.values,index=d.rel).sort_index()
DW=pd.DataFrame(dd); DM=DW.resample("ME").last(); dDM=DM.diff()
print("drought states",DW.shape, DW.index.min(), DW.index.max())
reg=lambda s: dDM[[x for x in s if x in dDM]].mean(1)
CB=reg("IA IL IN NE MN".split()); PL=reg("IA NE KS SD ND MN".split()); WE=reg("WA OR ID CA MT".split()); CA=dDM["CA"]; SPL=reg("TX OK KS NM".split())
gs=lambda s: s[s.index.month.isin(range(4,10))]
def bask(tk): tk=[t for t in tk if t in MX]; return MX[tk].mean(1)
banks=[t for t in ST.index if ST[t] in "IA NE KS SD ND MN".split() and 6020<=SIC.get(t,0)<=6029]
print("farm-state banks",banks)
y1=lambda b: b.shift(-1)       # next-month return aligned to signal month
SP="2016-01-01"
regrow("P2_Drought","DR1 Corn Belt ΔD2+ (Apr-Sep) -> ag equipment DE/AGCO/LNN/TITN",-1,gs(y1(bask("DE AGCO LNN TITN".split()))),gs(CB),SP,"USDA ERS farm income; Ortiz-Bobea et al. 2021")
regrow("P2_Drought","DR2 Corn Belt ΔD2+ (Apr-Sep) -> grain merchandisers ADM/BG",-1,gs(y1(bask(["ADM","BG"]))),gs(CB),SP,"")
regrow("P2_Drought","DR3 Corn Belt ΔD2+ (Apr-Sep) -> rails UNP/CSX/NSC",-1,gs(y1(bask(["UNP","CSX","NSC"]))),gs(CB),SP,"AAR grain carloads")
regrow("P2_Drought","DR4 Corn Belt ΔD2+ (Apr-Sep) -> fertilizer CF/MOS/NTR",-1,gs(y1(bask(["CF","MOS","NTR"]))),gs(CB),SP,"")
regrow("P2_Drought",f"DR5 Plains ΔD2+ -> farm-state HQ banks (n={len(banks)})",-1,y1(bask(banks)),PL,SP,"KC Fed ag credit survey")
regrow("P2_Drought","DR6 West ΔD2+ -> hydro-exposed utilities IDA/AVA/POR/NWE/PCG/EIX",-1,y1(bask("IDA AVA POR NWE PCG EIX".split())),WE,SP,"Gleick 2016 (CA drought hydropower costs)")
regrow("P2_Drought","DR7 CA ΔD2+ -> CA water utilities CWT/HTO(SJW)/AWR",-1,y1(bask(["CWT","AWR","HTO","SJW"])),CA,SP,"CA 2015 conservation mandate")
# DR8 cross-sectional
stocks=[t for t in UNIV if t in ST.index]
sig=pd.DataFrame({t:dDM[ST[t]] for t in stocks if ST[t] in dDM}); sig=sig[sig.index>="2011-01-01"]
ls8=tercile_ls(sig,high_long=False); lsrow("P2_Drought","DR8 HQ-state ΔD2+: long low-Δdrought-state minus high tercile (universe)",1,ls8,"2019-01-01","Korniotis-Kumar local demand")
# ---------- EN own ideas
LN=(oni<=-0.5).astype(float); EN=(oni>=0.5).astype(float)
d=regrow("P2_ENSOxState","EN1 La Niña (lag1) -> next-month ΔD2+ Southern Plains TX/OK/KS/NM (physical first stage)",1,SPL.shift(-1),LN.reindex(SPL.index),SP,"NOAA CPC ENSO teleconnections",unit="pp change in % area D2+",scale=1)
energy=[t for t in ST.index if ST[t] in "TX OK ND LA CO".split() and SIC.get(t,0) in (1311,1381,1389,2911) and t in UNIV]
print("energy-state firms",energy)
regrow("P2_ENSOxState",f"EN2 La Niña -> energy firms HQ TX/OK/ND/LA/CO (n={len(energy)}) excess ret",1,y1(bask(energy)),LN.reindex(MX.index),"2019-01-01","Phase 1 crude-in-La-Niña survivor",unit="% next-month excess, La Niña minus other")
regrow("P2_ENSOxState","EN3 La Niña -> PNW hydro utilities IDA/AVA/POR",1,y1(bask(["IDA","AVA","POR"])),LN.reindex(MX.index),SP,"NOAA CPC; BPA hydro",unit="% next-month excess, La Niña minus other")
regrow("P2_ENSOxState","EN4 El Niño -> farm-state HQ banks",-1,y1(bask(banks)),EN.reindex(MX.index),SP,"Phase 1 fertilizer-in-El-Niño survivor",unit="% next-month excess, El Niño minus other")
yy=gs(y1(bask("DE AGCO LNN TITN".split()))); xx=gs(CB); xx=(xx-xx.mean())/xx.std(); en=EN.reindex(xx.index)
Z=pd.concat([yy,xx,en,xx*en],axis=1).dropna(); Z.columns=["y","x","en","int"]
def nwX(Z): return nw(Z.y,Z[["x","en","int"]],6)
f=nwX(Z); i=nwX(Z[Z.index<SP]); oo=nwX(Z[Z.index>=SP])
add("P2_ENSOxState","EN5 Corn Belt drought × El Niño interaction -> ag equipment",-1,f[3],f[0]*100,"% interaction coef per 1sd",f[1],f[2],i[0]*100,i[1],oo[0]*100,oo[1],oo[2],"own",start=str(Z.index.min().date()),split=SP)
# ---------- Local bias
ci=pd.DataFrame({s:pd.read_csv(f"data/state/fred_{s}PHCI.csv",index_col=0,parse_dates=True).iloc[:,0] for s in US if s!="DC" and __import__("os").path.exists(f"data/state/fred_{s}PHCI.csv")})
ci.index=ci.index+pd.offsets.MonthEnd(0); g3=ci.pct_change(3).shift(2)   # 2-month publication lag
sig=pd.DataFrame({t:g3[ST[t]] for t in stocks if ST[t] in g3}); sig=sig[sig.index>="2011-01-01"]
lb1=tercile_ls(sig,high_long=False); lsrow("P2_LocalBias","LB1 State coincident-index 3m growth (lag 2m): long weak-state minus strong-state terciles",1,lb1,"2019-01-01","Korniotis & Kumar 2013 JF")
cl=pd.DataFrame({s:pd.read_csv(f"data/state/fred_{s}ICLAIMS.csv",index_col=0,parse_dates=True).iloc[:,0] for s in US if __import__("os").path.exists(f"data/state/fred_{s}ICLAIMS.csv")})
c4=cl.rolling(4).mean(); cy=c4.pct_change(52,fill_method=None); cy.index=cy.index+pd.Timedelta(days=14)
cym=cy.resample("ME").last()
sig=pd.DataFrame({t:cym[ST[t]] for t in stocks if ST[t] in cym}); sig=sig[sig.index>="2011-01-01"].clip(-5,5)
lb2=tercile_ls(sig,high_long=True); lsrow("P2_LocalBias","LB2 State initial-claims YoY (4wk avg, lag 2w): long high-claims-growth minus low terciles",1,lb2,"2019-01-01","Korniotis & Kumar 2013 JF")
Mu=M[[t for t in stocks if t in M]]; Mu=Mu[Mu.index>="2011-01-01"]
stg=pd.Series({t:ST[t] for t in Mu}); big=stg.value_counts(); big=big[big>=5].index
sums=Mu.T.groupby(stg).sum().T; cnts=Mu.notna().T.groupby(stg).sum().T
peer=pd.DataFrame({t:(sums[stg[t]]-Mu[t].fillna(0))/(cnts[stg[t]]-Mu[t].notna()) for t in Mu if stg[t] in big})
res=peer.copy()
for dt in peer.index:   # residualize on own return
    a=pd.concat([peer.loc[dt],Mu.loc[dt,peer.columns]],axis=1).dropna()
    if len(a)>30: b=np.polyfit(a.iloc[:,1],a.iloc[:,0],1); res.loc[dt,a.index]=a.iloc[:,0]-np.polyval(b,a.iloc[:,1])
lb3=tercile_ls(res,high_long=True); lsrow("P2_LocalBias","LB3 Same-HQ-state peer return last month (own-ret residualized): long top minus bottom tercile",1,lb3,"2019-01-01","Parsons, Sabbatucci & Titman 2020 RFS; Pirinsky & Wang 2006 JF")
# LB4 descriptive comovement
betas=[]
for t in peer.columns:
    a=pd.concat([Mu[t],peer[t],M["SPY"]],axis=1).dropna()
    if len(a)>36: betas.append(sm.OLS(a.iloc[:,0],sm.add_constant(a.iloc[:,1:])).fit().params.iloc[1])
betas=pd.Series(betas); CASE.append(dict(id="LB4",desc="Own-state peer beta controlling for SPY (Pirinsky-Wang comovement), monthly 2011-2026",value=f"median {betas.median():.3f}, mean {betas.mean():.3f}, share>0 {(betas>0).mean():.2f}, n={len(betas)}"))
# ---------- Politics
D12="CA OR WA NV CO NM MN IA WI MI IL OH PA VA MD DE NJ NY CT RI MA VT NH ME FL HI DC".split()
D16="CA OR WA NV CO NM MN IL VA MD DE NJ NY CT RI MA VT NH ME HI DC".split()
D20=D16+"AZ GA MI PA WI".split(); D24=[s for s in D16 if s!="NV"]
def aligned(dt):
    y=dt.year
    if y<=2016: return set(D12)          # Obama (D)
    if y<=2020: return US-set(D16)       # Trump (R)
    if y<=2024: return set(D20)          # Biden (D)
    return US-set(D24)                   # Trump (R)
ls={}
for dt in Mu.index:
    if dt<pd.Timestamp("2013-01-31"): continue
    al=aligned(dt); r=Mu.loc[dt].dropna(); a=[t for t in r.index if stg[t] in al]; b=[t for t in r.index if stg[t] not in al]
    ls[dt]=r[a].mean()-r[b].mean()-0.001*2*(dt.month==1 and dt.year in (2017,2021,2025))
lsrow("P2_Politics","PO1 Aligned-with-President's-party HQ states minus non-aligned, eq-wt",1,pd.Series(ls),"2019-01-01","Kim, Pantzalis & Park 2012 JFE")
DX=P.pct_change(fill_method=None)
def bevent(fam,hyp,pred,dates,basket,h,src,signs=None,cost=0.002,lag=1,split="2019-01-01",prereg=True):
    cars=[];ds=[]
    signs=signs or [1]*len(dates)
    for d,sg in zip(dates,signs):
        k=P.index.searchsorted(pd.Timestamp(d),side="right")+lag-1
        tk=[t for t in basket if t in DX and pd.notna(P[t].iloc[k])]
        if not tk or k+h>=len(P): continue
        ar=(DX[tk].iloc[k+1:k+h+1].mean(1)-DX["SPY"].iloc[k+1:k+h+1]).sum()
        cars.append(sg*ar-cost); ds.append(P.index[k])
    c=pd.Series(cars,index=ds)
    def st(x): 
        if len(x)<2: return (x.mean()*100 if len(x) else np.nan),np.nan,np.nan
        tt=x.mean()/(x.std(ddof=1)/np.sqrt(len(x))); from scipy import stats; return x.mean()*100,tt,2*stats.t.sf(abs(tt),len(x)-1)
    f=st(c); i=st(c[c.index<split]); o=st(c[c.index>=split])
    if prereg: add(fam,hyp,pred,len(c),f[0],f"% CAR [+1,+{h}] net of {cost*1e4:.0f}bp vs SPY",f[1],f[2],i[0],i[1],o[0],o[1],o[2],src,"basket-event",start=str(min(ds).date()) if ds else None,split=split)
    return c
CANN=["CGC","TLRY","ACB","CRON","MSOS"]
c=bevent("P2_Politics","PO2 Recreational cannabis ballot election (wins +, 2024 all-fail −) -> cannabis basket",1,["2016-11-08","2018-11-06","2020-11-03","2022-11-08","2023-11-07","2024-11-05"],CANN,5,"Event studies of cannabis equities around elections",signs=[1,1,1,1,1,-1])
MED=["2017-11-07","2018-11-06","2020-06-30","2020-08-04","2022-11-08"]
bevent("P2_Politics","PO3 Medicaid expansion ballot approvals -> hospitals HCA/UHS/THC/CYH",1,MED,["HCA","UHS","THC","CYH"],5,"Dranove, Garthwaite & Ody 2016")
bevent("P2_Politics","PO4 Medicaid expansion ballot approvals -> Medicaid insurers CNC/MOH",1,MED,["CNC","MOH"],5,"Kaestner et al. 2017")
for nm,dt,bk,h,lg in [("PO5 CA AB1228 $20 fast-food wage signed 2023-09-28, restaurants",["2023-09-28"],"CMG MCD YUM JACK WING SBUX".split(),5,0),
                    ("PO6 Murphy v NCAA 2018-05-14, gaming",["2018-05-11"],"PENN CZR MGM BYD CHDN".split(),1,1),
                    ("ND6 Texas freeze 2021-02-12..+10d, TX power/gas",["2021-02-11"],"VST NRG CNP ATO AEP".split(),10,1)]:
    c=bevent("","",0,dt,bk,h,"",cost=0,lag=lg,prereg=False); CASE.append(dict(id=nm.split()[0],desc=nm+f", [+1,+{h}] CAR vs SPY",value=f"{c.iloc[0]*100:.2f}%" if len(c) else "n/a"))
# ---------- Federal spending
A=pd.read_csv("data/state/usaspending_awards_1bn.csv")
MAP=[("LOCKHEED","LMT"),("SIKORSKY","LMT"),("BOEING","BA"),("RAYTHEON|RTX|PRATT & WHITNEY|COLLINS AEROSPACE","RTX"),("NORTHROP","NOC"),("HUNTINGTON INGALLS|NEWPORT NEWS","HII"),
     ("GENERAL DYNAMICS|ELECTRIC BOAT|BATH IRON|NATIONAL STEEL AND SHIP","GD"),("L3HARRIS|HARRIS CORP","LHX"),("LEIDOS","LDOS"),("BOOZ ALLEN","BAH"),("SCIENCE APPLICATIONS","SAIC"),
     ("CACI","CACI"),("HUMANA","HUM"),("MCKESSON","MCK"),("OPTUM|UNITEDHEALTH","UNH"),("GENERAL ELECTRIC","GE"),("HONEYWELL","HON"),("BWX","BWXT"),("KBR","KBR"),("PFIZER","PFE"),("MERCK","MRK"),
     ("OSHKOSH","OSK"),("TEXTRON|BELL TEXTRON","TXT"),("CENTENE|HEALTH NET","CNC"),("CARDINAL HEALTH","CAH"),("AMERISOURCE|CENCORA","COR"),("MODERNA","MRNA"),("JOHNSON & JOHNSON|JANSSEN","JNJ"),("ABBOTT","ABT"),("DELL","DELL"),("MICROSOFT","MSFT"),("AMAZON","AMZN"),("JACOBS","J"),("FLUOR","FLR"),("PARSONS","PSN"),("ACCENTURE","ACN"),("IBM|INTERNATIONAL BUSINESS MACHINES","IBM")]
def mp(n):
    if re.search(r"\bJV\b|JOINT|ALLIANCE|LLC JV",n): return None
    for pat,t in MAP:
        if re.search(pat,n): return t
A["sym"]=A["Recipient Name"].astype(str).map(mp); A["date"]=pd.to_datetime(A["Base Obligation Date"],errors="coerce")
A=A.dropna(subset=["sym","date"]); A=A[A.date>="2011-02-01"]
ev=A.drop_duplicates(["sym","date"]); print("FS events",len(ev),ev.sym.value_counts().head(10).to_dict())
def ctrow(fam,hyp,pred,evs,h,src,sign=1):
    r=calendar_time(evs[["sym","date"]],h,sign=sign,px_df=P)
    if r is None: return
    add(fam,hyp,pred,r["n"],r["car_mean"],f"% CAR [+1,+{h}] net of 20bp vs SPY (calendar-time t)",r["t"],r["p"],r["car_is"],r["t_is"],r["car_oos"],r["t_oos"],r["p_oos"],src,"event-ct",start=str(evs.date.min().date()),split="2019-01-01")
    return r
ctrow("P2_FedSpend","FS1 USAspending prime award ≥$1bn (base obligation date) -> recipient",1,ev,5,"McGowan & Vendrzyk 2002")
ctrow("P2_FedSpend","FS2 USAspending prime award ≥$5bn -> recipient",1,A[A["Award Amount"]>=5e9].drop_duplicates(["sym","date"]),5,"McGowan & Vendrzyk 2002")
# ---------- Disasters
fe=pd.read_csv("data/state/fema_declarations.csv",parse_dates=["declarationDate"]); fe["declarationDate"]=fe.declarationDate.dt.tz_localize(None).dt.normalize()
first=fe.sort_values("declarationDate").drop_duplicates("disasterNumber")
DR=first[first.declarationType=="DR"]; DR=DR[DR.declarationDate>="2000-01-01"]
print("FEMA DR disasters",len(DR))
util=[t for t in ST.index if 4900<=SIC.get(t,0)<=4949 and t in P]; bk=[t for t in ST.index if 6020<=SIC.get(t,0)<=6029 and t in P]
def st_events(stk):
    e=[(t,d) for st_,d in zip(DR.state,DR.declarationDate) for t in stk if ST[t]==st_]
    return pd.DataFrame(e,columns=["sym","date"]).drop_duplicates()
ctrow("P2_Disaster","ND1 FEMA major-disaster declaration -> utilities HQ in declared state",-1,st_events(util),20,"utility storm-cost event studies")
ctrow("P2_Disaster","ND2 FEMA major-disaster declaration -> banks HQ in declared state",-1,st_events(bk),20,"Cortés & Strahan 2017 JFE")
hu=DR[(DR.incidentType=="Hurricane")&DR.state.isin(["FL","TX","LA","NC","SC"])].sort_values("declarationDate")
hd=hu.declarationDate[hu.declarationDate.diff().dt.days.fillna(99)>7].tolist(); print("hurricane event dates",len(hd))
bevent("P2_Disaster","ND3 Hurricane DR in FL/TX/LA/NC/SC -> P&C insurers",-1,hd,"TRV ALL CB PGR HIG CINF WRB AIG".split(),5,"cat-loss event studies",split=SP)
bevent("P2_Disaster","ND4 Hurricane DR in FL/TX/LA/NC/SC -> homebuilders",1,hd,"DHI LEN PHM NVR TOL KBH".split(),60,"rebuilding demand",split=SP)
cf=fe[(fe.state=="CA")&(fe.incidentType=="Fire")&fe.declarationType.isin(["DR","FM"])].drop_duplicates("disasterNumber")
fd=sorted(set(cf.declarationDate)); print("CA fire declaration dates",len(fd))
bevent("P2_Disaster","ND5 CA fire DR/FM declarations -> PCG/EIX",-1,fd,["PCG","EIX"],5,"PG&E 2019 bankruptcy; inverse condemnation",split=SP)
R=pd.DataFrame(rows); R.to_csv("results/state_signals.csv",index=False); pd.DataFrame(CASE).to_csv("results/state_case_studies.csv",index=False)
pd.set_option("display.width",250); print(R[["hyp","pred_sign","n","effect","t","p","eff_is","eff_oos","t_oos","dir_ok"]].round(3).to_string()); print(pd.DataFrame(CASE).to_string())
# charts
fig,ax=plt.subplots(2,1,figsize=(11,6)); DM[["IA","IL","NE","CA","TX"]].plot(ax=ax[0]); ax[0].set_title("US Drought Monitor % area D2+ (month-end)")
for nm,s in [("DR8",ls8),("LB1",lb1),("LB2",lb2),("LB3",lb3),("PO1",pd.Series(ls))]: s.dropna().cumsum().plot(ax=ax[1],label=nm)
ax[1].legend(); ax[1].set_title("Cumulative monthly L-S (net)"); fig.tight_layout(); fig.savefig("charts/state_signals.png",dpi=110)
