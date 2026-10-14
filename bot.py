import os, time, requests, pandas as pd
from datetime import datetime
BOT_TOKEN=os.getenv("BOT_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")
SYMBOLS={"EURUSD":"EURUSD=X","GBPUSD":"GBPUSD=X","USDCHF":"USDCHF=X","USDJPY":"USDJPY=X","USDCNH":"USDCNH=X","USDRUB":"USDRUB=X","AUDUSD":"AUDUSD=X","NZDUSD":"NZDUSD=X","GOLD":"GC=F","BTC":"BTC-USD"}
def send_telegram(msg):
 if not BOT_TOKEN or not CHAT_ID: return
 try:
  url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  requests.post(url,data={"chat_id":CHAT_ID,"text":msg,"parse_mode":"Markdown"},timeout=10)
 except: pass
def get_data(sym):
 try:
  url=f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=1y"
  r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=15).json()
  closes=r['chart']['result'][0]['indicators']['quote'][0]['close']
  closes=[x for x in closes if x is not None]
  if len(closes)<30: return None,None
  df=pd.DataFrame(closes,columns=['close'])
  df['ema21']=df['close'].ewm(span=21).mean()
  return df['close'].iloc[-1],df['ema21'].iloc[-1]
 except: return None,None
send_telegram("✅ *BIBLE BOT 24/7 IS LIVE!*\nWatching 10: EURUSD GBPUSD USDCHF USDJPY USDCNH USDRUB AUDUSD NZDUSD GOLD BTC\nScanning EMA21 every 2 mins")
while True:
 for name,ys in SYMBOLS.items():
  p,e=get_data(ys)
  if p is None: time.sleep(2); continue
  dist=abs(p-e)/e*100
  if dist<0.8:
   send_telegram(f"📊 *{name} NEAR EMA21!*\nPrice:{p:.5f}\nEMA21:{e:.5f}\nDist:{dist:.2f}%\nTime:{datetime.now().strftime('%H:%M')}")
  time.sleep(1.5)
 time.sleep(120)
