import pandas as pd, numpy as np
A=pd.read_csv("results/ALL_HYPOTHESES_ranked.csv")
def f(x,d=2): return "" if pd.isna(x) else f"{x:+.{d}f}"
top=A.head(30)
tbl="| # | Family | Hypothesis | n | Effect (full) | Unit | t | BH q | IS effect | OOS effect (t) | BH ✓ | OOS ✓ |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n"
for i,(_,r) in enumerate(top.iterrows(),1):
    tbl+=f"| {i} | {r.family} | {r.hyp} | {int(r.n)} | {f(r.effect)} | {r.unit} | {r.t:.2f} | {r.q_BH:.3f} | {f(r.eff_is)} | {f(r.eff_oos)} ({'' if pd.isna(r.t_oos) else f'{r.t_oos:.1f}'}) | {'✅' if r.survives_BH else '—'} | {'✅' if r.oos_confirms else '—'} |\n"
fam=A.groupby("family").agg(hyps=("hyp","size"),p_lt_05=("p",lambda p:(p<0.05).sum()),survive_BH=("survives_BH","sum")).reset_index()
fam["expected_p<.05_by_chance"]=(fam.hyps*0.05).round(1)
open("README.md","w").write(open("README.template.md").read().replace("{{TABLE}}",tbl).replace("{{FAM}}",fam.to_markdown(index=False)).replace("{{N}}",str(len(A))).replace("{{NBH}}",str(int(A.survives_BH.sum()))))
