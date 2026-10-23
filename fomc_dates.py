import re,glob,pandas as pd
out=[]
for f in sorted(glob.glob("data/fomc_19*.html")+glob.glob("data/fomc_20*.html")):
    y=int(re.findall(r"\d{4}",f)[0]); t=open(f).read()
    for m in re.findall(r"<h5[^>]*>([A-Za-z]+)\s+(\d+)(?:-(\d+))?\s+Meeting[^<]*</h5>",t):
        mon,d1,d2=m; d=int(d2 or d1)
        try: out.append(pd.Timestamp(f"{mon} {d} {y}"))
        except: pass
t=open("data/fomc_cur.html").read()
for blk in re.split(r'<h4><a id="\d+">',t)[1:]:
    y=int(re.match(r"(\d{4})",blk).group(1))
    for mon,days in re.findall(r'fomc-meeting__month[^>]*><strong>([A-Za-z/]+)</strong>.*?fomc-meeting__date[^>]*>([\d\-\*]+)',blk,re.S):
        mon=mon.split("/")[-1]; d=int(re.findall(r"\d+",days)[-1])
        try: out.append(pd.Timestamp(f"{mon} {d} {y}"))
        except: pass
s=pd.Series(sorted(set(out))); s=s[s<=pd.Timestamp("2026-10-23")]
s.to_csv("data/fomc_dates.csv",index=False); print(len(s), s.min(), s.max()); print(s.dt.year.value_counts().sort_index().to_string())
