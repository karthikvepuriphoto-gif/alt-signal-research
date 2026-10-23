import sys; sys.path.insert(0,"lib")
from common import *
F=["enso_lag1_thr0.5","hurricane","calendar","insider","events_b","congress","trump","musk","wsb","state_signals"]
D=pd.concat([pd.read_csv(f"results/{f}.csv").assign(file=f) for f in F],ignore_index=True)
D["q_BH"]=bh(D.p.values)
D["survives_BH"]=D.q_BH<0.05
D["oos_confirms"]=(np.sign(D.eff_is)==np.sign(D.eff_oos))&(D.p_oos<0.10)
D["small_sample"]=D.n<30
D=D.sort_values("p"); D.to_csv("results/ALL_HYPOTHESES_ranked.csv",index=False)
print("total hypotheses",len(D),"by family",D.family.value_counts().to_dict())
print("survive BH",D.survives_BH.sum(),"survive BH & OOS confirm",(D.survives_BH&D.oos_confirms).sum())
pd.set_option("display.width",250)
print(D[D.survives_BH|((D.q_BH<0.2))][["family","hyp","n","effect","unit","t","p","q_BH","eff_is","eff_oos","t_oos","oos_confirms"]].to_string())
