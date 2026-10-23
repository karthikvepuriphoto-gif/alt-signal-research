import pandas as pd, zipfile, glob, io
out=[]
for f in sorted(glob.glob("data/form345/*.zip")):
    z=zipfile.ZipFile(f)
    rd=lambda n,c: pd.read_csv(z.open(n),sep="\t",usecols=c,dtype=str,on_bad_lines="skip",quoting=3)
    s=rd("SUBMISSION.tsv",["ACCESSION_NUMBER","FILING_DATE","DOCUMENT_TYPE","ISSUERTRADINGSYMBOL"])
    t=rd("NONDERIV_TRANS.tsv",["ACCESSION_NUMBER","TRANS_DATE","TRANS_CODE","TRANS_SHARES","TRANS_PRICEPERSHARE","TRANS_ACQUIRED_DISP_CD"])
    o=rd("REPORTINGOWNER.tsv",["ACCESSION_NUMBER","RPTOWNERCIK","RPTOWNER_RELATIONSHIP"])
    t=t[(t.TRANS_CODE=="P")&(t.TRANS_ACQUIRED_DISP_CD=="A")]
    m=t.merge(s[s.DOCUMENT_TYPE.isin(["4","4/A"])],on="ACCESSION_NUMBER").merge(o.drop_duplicates("ACCESSION_NUMBER"),on="ACCESSION_NUMBER")
    out.append(m); print(f,len(m),flush=True)
d=pd.concat(out); d["value"]=pd.to_numeric(d.TRANS_SHARES,errors="coerce")*pd.to_numeric(d.TRANS_PRICEPERSHARE,errors="coerce")
d["FILING_DATE"]=pd.to_datetime(d.FILING_DATE,format="%d-%b-%Y",errors="coerce"); d["TRANS_DATE"]=pd.to_datetime(d.TRANS_DATE,format="%d-%b-%Y",errors="coerce")
d["sym"]=d.ISSUERTRADINGSYMBOL.str.upper().str.strip()
d.to_parquet("data/insider_purchases.parquet"); print(len(d))
