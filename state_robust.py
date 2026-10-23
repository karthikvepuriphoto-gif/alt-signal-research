# Exploratory (not preregistered) robustness for the significant cross-sectional results: drop the largest HQ states
exec(open('state_tests.py').read().split('# ---------- Politics')[0])
out=[]
for drop in [[],["CA"],["CA","TX"],["CA","TX","NY"]]:
    keep=[t for t in stocks if ST[t] not in drop]
    s=pd.DataFrame({t:dDM[ST[t]] for t in keep if ST[t] in dDM}); s=s[s.index>="2011-01-01"]
    r=tercile_ls(s,high_long=False); out.append(("DR8",",".join(drop) or "none",*np.round(nw(r.dropna(),None,6)[:2],4)))
    s=pd.DataFrame({t:cym[ST[t]] for t in keep if ST[t] in cym}); s=s[s.index>="2011-01-01"].clip(-5,5)
    r=tercile_ls(s,high_long=True); out.append(("LB2",",".join(drop) or "none",*np.round(nw(r.dropna(),None,6)[:2],4)))
    # PO1
    D12="CA OR WA NV CO NM MN IA WI MI IL OH PA VA MD DE NJ NY CT RI MA VT NH ME FL HI DC".split();D16="CA OR WA NV CO NM MN IL VA MD DE NJ NY CT RI MA VT NH ME HI DC".split();D20=D16+"AZ GA MI PA WI".split();D24=[x for x in D16 if x!="NV"]
    al=lambda y: set(D12) if y<=2016 else (US-set(D16) if y<=2020 else (set(D20) if y<=2024 else US-set(D24)))
    ls={}
    for dt in Mu.index:
        if dt<pd.Timestamp("2013-01-31"): continue
        rr=Mu.loc[dt,[t for t in Mu if ST[t] not in drop]].dropna(); A_=al(dt.year)
        ls[dt]=rr[[t for t in rr.index if ST[t] in A_]].mean()-rr[[t for t in rr.index if ST[t] not in A_]].mean()
    out.append(("PO1",",".join(drop) or "none",*np.round(nw(pd.Series(ls),None,6)[:2],4)))
# PO1 industry-neutral: within 2-digit SIC
ls={}
for dt in Mu.index:
    if dt<pd.Timestamp("2013-01-31"): continue
    rr=Mu.loc[dt].dropna(); A_=al(dt.year); df=pd.DataFrame({"r":rr,"a":[ST[t] in A_ for t in rr.index],"ind":[int(np.nan_to_num(SIC.get(t,0)))//100 for t in rr.index]})
    df["r"]=df.r-df.groupby("ind").r.transform("mean"); ls[dt]=df[df.a].r.mean()-df[~df.a].r.mean()
out.append(("PO1","industry-neutral (SIC2 demeaned)",*np.round(nw(pd.Series(ls),None,6)[:2],4)))
for nm in ["DR8","LB2"]:
    pass
R=pd.DataFrame(out,columns=["test","dropped_states","mean_monthly","t"]); R.to_csv("results/state_robustness.csv",index=False); print(R)
