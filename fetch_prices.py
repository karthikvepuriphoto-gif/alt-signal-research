import yfinance as yf, pandas as pd, warnings; warnings.filterwarnings("ignore")
T="^GSPC SPY ZC=F ZW=F KC=F NG=F SB=F CL=F ZS=F CC=F EWA EWZ INDA EPU EWW ECH EIDO EWM KIE XLU XLE XLF XLB IYR ITB XHB CF MOS NTR RNR EG ACGL TRV ALL PGR CB LEN DHI PHM NVR HD LOW BDRY ZIM MATX ^AXJO ^BVSP ^BSESN ^VIX TSLA GME AMC DOGE-USD BTC-USD QQQ IWM ^RUT".split()
df=yf.download(T,start="1927-01-01",auto_adjust=True,progress=False)["Close"]
df.to_csv("data/prices.csv"); print(df.notna().idxmax().to_string())
