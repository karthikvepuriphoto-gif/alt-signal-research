import pandas as pd, numpy as np
A=pd.read_csv("results/ALL_HYPOTHESES_ranked.csv"); top=A[(A.family=="A_ENSO")&(A.q_BH<0.2)].hyp.tolist()
specs={"lag1_thr0.5 (primary, realistic)":"enso_lag1_thr0.5","lag2_thr0.5":"enso_lag2_thr0.5","lag3_thr0.5":"enso_lag3_thr0.5","lag1_thr1.0 (strong events)":"enso_lag1_thr1.0"}
R=[]
for h in top:
    row={"hyp":h}
    for k,f in specs.items():
        d=pd.read_csv(f"results/{f}.csv"); hh=h.replace("0.5","1.0") if "thr1.0" in f else h
        x=d[d.hyp==hh]
        row[k]=f"{x.effect.iloc[0]:+.2f} (t={x.t.iloc[0]:.1f})" if len(x) else "n/a"
    R.append(row)
R=pd.DataFrame(R); R.to_csv("results/enso_robustness_specs.csv",index=False); print(R.to_string())
