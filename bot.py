import os, time, requests, pandas as pd
from datetime import datetime
BOT_TOKEN=os.getenv("BOT_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")

# YOUR 10 MARKETS - ALL INCLUDED
SYMBOLS={
 "EURUSD":"EURUSD=X",
 "GBPUSD":"GBPUSD=X",
 "USDCHF":"USDCHF=X",
 "USDJPY":"USDJPY=X",
 "USDCNH":"USDCNH=X",
 "USDRUB":"USDRUB=X",
 "AUDUSD":"AUDUSD=X",
 "NZDUSD":"NZDUSD=X",
 "GOLD":"GC=F",
 "BTC":"BTC-USD"
}

last_alert={}

def send_telegram(msg):
 try:
  url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  requests.post(url,data={"chat_id":CHAT_ID,"text":msg,"parse_mode":"Markdown"},timeout=15)
 except: pass

def get_bible_signal(yahoo_sym):
 try:
  url=f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_sym}?interval=1d&range=3mo"
  r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=15).json()
  result=r['chart']['result'][0]
  closes=result['indicators']['quote'][0]['close']
  opens=result['indicators']['quote'][0]['open']
  highs=result['indicators']['quote'][0]['high']
  lows=result['indicators']['quote'][0]['low']
  data=[]
  for o,h,l,c in zip(opens,highs,lows,closes):
   if None not in (o,h,l,c): data.append((o,h,l,c))
  if len(data)<30: return None
  df=pd.DataFrame(data,columns=['open','high','low','close'])
  df['ema21']=df['close'].ewm(span=21).mean()
  last=df.iloc[-1]
  price=last['close']
  ema=last['ema21']
  dist=abs(price-ema)/ema*100
  if dist>0.9: return None
  o,h,l,c = last['open'],last['high'],last['low'],last['close']
  body=abs(c-o)
  if body==0: body=0.0001
  upper_wick=h-max(o,c)
  lower_wick=min(o,c)-l
  is_pin_bull = lower_wick > 2*body and upper_wick < body
  is_pin_bear = upper_wick > 2*body and lower_wick < body
  signal=None
  if is_pin_bull: signal="BUY"
  if is_pin_bear: signal="SELL"
  if not signal: return None
  return {"price":price,"ema":ema,"dist":dist,"signal":signal,"high":h,"low":l}
 except:
  return None

send_telegram("🔥 *BIBLE BOT LIVE - ALL 10 MARKETS*\nEURUSD GBPUSD USDCHF USDJPY USDCNH USDRUB AUDUSD NZDUSD GOLD BTC\nMode: BUY/SELL Pin Bar at EMA21")

while True:
 for name,ys in SYMBOLS.items():
  sig=get_bible_signal(ys)
  if sig:
   now=time.time()
   if name not in last_alert or now-last_alert[name]>14400:
    sl = sig['low']*0.999 if sig['signal']=="BUY" else sig['high']*1.001
    emoji="🟢" if sig['signal']=="BUY" else "🔴"
    msg=f"{emoji} *{sig['signal']} SIGNAL {name}* {emoji}\n\n*Pair:* {name}\n*Signal:* {sig['signal']} @ {sig['price']:.5f}\n*EMA21:* {sig['ema']:.5f}\n*Setup:* D1 Pin Bar at EMA21\n*Stop Loss:* {sl:.5f}\n*Dist:* {sig['dist']:.2f}%\n\nTime: {datetime.now().strftime('%d %b %H:%M')} EAT"
    send_telegram(msg)
    last_alert[name]=now
  time.sleep(2)
 time.sleep(180)
