import requests, json, os, time, pandas as pd, io
from concurrent.futures import ThreadPoolExecutor
UA={"User-Agent":"Karthik Vepuri research karthikvepuriphoto@gmail.com"}
F={'AL':1,'AK':2,'AZ':4,'AR':5,'CA':6,'CO':8,'CT':9,'DE':10,'DC':11,'FL':12,'GA':13,'HI':15,'ID':16,'IL':17,'IN':18,'IA':19,'KS':20,'KY':21,'LA':22,'ME':23,'MD':24,'MA':25,'MI':26,'MN':27,'MS':28,'MO':29,'MT':30,'NE':31,'NV':32,'NH':33,'NJ':34,'NM':35,'NY':36,'NC':37,'ND':38,'OH':39,'OK':40,'OR':41,'PA':42,'RI':44,'SC':45,'SD':46,'TN':47,'TX':48,'UT':49,'VT':50,'VA':51,'WA':53,'WV':54,'WI':55,'WY':56}
# 1 drought
def dr(st):
    p=f"data/state/usdm_{st}.csv"
    if os.path.exists(p) and os.path.getsize(p)>1000: return
    r=requests.get(f"https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi={F[st]:02d}&startdate=1/1/2000&enddate=10/20/2026&statisticsType=1",timeout=120)
    open(p,"w").write(r.text)
with ThreadPoolExecutor(4) as ex: list(ex.map(dr,F))
print("drought done",flush=True)
# 2 FRED state coincident index + initial claims
def fred(s):
    p=f"data/state/fred_{s}.csv"
    if os.path.exists(p): return
    for _ in range(3):
        try:
            r=requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}",timeout=60)
            if r.ok and r.text.startswith("observation_date"): open(p,"w").write(r.text); return
        except Exception: time.sleep(2)
with ThreadPoolExecutor(4) as ex: list(ex.map(fred,[f"{s}PHCI" for s in F if s!="DC"]+[f"{s}ICLAIMS" for s in F]))
print("fred done",flush=True)
# 3 EDGAR HQ state
T=list(pd.read_parquet("data/eq_adj.parquet").columns)
extra="DE AGCO ADM BG UNP CSX NSC CF MOS NTR CTVA FMC LNN TITN AWK CWT SJW AWR WTRG MSEX YORW IDA AVA POR PCG EIX NWE HCA UHS THC CYH CNC MOH ELV UNH MSOS CGC TLRY DKNG PENN MGM CZR WYNN LVS BYD CHDN RRR".split()
T=sorted(set(T+extra))
ct=requests.get("https://www.sec.gov/files/company_tickers.json",headers=UA).json(); m={v["ticker"].replace(".","-"):v["cik_str"] for v in ct.values()}
rows=[]
for t in T:
    c=m.get(t)
    if not c: rows.append(dict(ticker=t)); continue
    p=f"data/state/sub_{c}.json"
    if not os.path.exists(p):
        r=requests.get(f"https://data.sec.gov/submissions/CIK{c:010d}.json",headers=UA,timeout=60); time.sleep(0.12)
        if not r.ok: rows.append(dict(ticker=t,cik=c)); continue
        j=r.json(); j={k:j.get(k) for k in ["name","sic","sicDescription","stateOfIncorporation","addresses"]}; json.dump(j,open(p,"w"))
    j=json.load(open(p)); a=(j.get("addresses") or {}).get("business",{}) or {}
    rows.append(dict(ticker=t,cik=c,name=j["name"],sic=j["sic"],sicDesc=j["sicDescription"],hq_state=a.get("stateOrCountry"),hq_city=a.get("city")))
pd.DataFrame(rows).to_csv("data/state/hq_states.csv",index=False); print("hq done",flush=True)
# 4 FEMA declarations
out=[];skip=0
while True:
    r=requests.get(f"https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$select=disasterNumber,state,declarationType,declarationDate,incidentType,incidentBeginDate,declarationTitle,designatedArea&$filter=declarationDate ge '2000-01-01'&$top=10000&$skip={skip}",timeout=120).json()
    d=r["DisasterDeclarationsSummaries"]; out+=d; skip+=10000
    if len(d)<10000: break
pd.DataFrame(out).to_csv("data/state/fema_declarations.csv",index=False); print("fema done",len(out),flush=True)
