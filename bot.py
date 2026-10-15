import os, time, requests, pandas as pd
from datetime import datetime

BOT_TOKEN=os.getenv("BOT_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")

# ONLY 8 CURRENCIES - GOLD AND BTC REMOVED
SYMBOLS={
 "EURUSD":"EURUSD=X",
 "GBPUSD":"GBPUSD=X",
 "USDCHF":"USDCHF=X",
 "USDJPY":"USDJPY=X",
 "USDCNH":"USDCNH=X",
 "USDRUB":"USDRUB=X",
 "AUDUSD":"AUDUSD=X",
 "NZDUSD":"NZDUSD=X"
}

last_alert={}

def send_telegram(msg):
 try:
  url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  requests.post(url,data={"chat_id":CHAT_ID,"text":msg,"parse_mode":"Markdown"},timeout=15)
 except: pass

def calc_rsi(closes, period=14):
 try:
  delta=pd.Series(closes).diff()
  gain=delta.where(delta>0,0).ewm(alpha=1/period).mean()
  loss=-delta.where(delta<0,0).ewm(alpha=1/period).mean()
  rs=gain/loss
  rsi=100-(100/(1+rs))
  return rsi.iloc[-1]
 except: return 50

def get_pro_signal(yahoo_sym):
 try:
  url=f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_sym}?interval=1d&range=4mo"
  r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=15).json()
  q=r['chart']['result'][0]['indicators']['quote'][0]
  closes=q['close']; opens=q['open']; highs=q['high']; lows=q['low']
  data=[]
  for o,h,l,c in zip(opens,highs,lows,closes):
   if None not in (o,h,l,c): data.append((o,h,l,c))
  if len(data)<35: return None
  df=pd.DataFrame(data,columns=['open','high','low','close'])
  df['ema21']=df['close'].ewm(span=21).mean()
  closes_list=df['close'].tolist()
  last=df.iloc[-1]
  price=last['close']; ema=last['ema21']

  # FILTER 1: Near EMA21 - 1% for more signals (both BUY and SELL)
  dist=abs(price-ema)/ema*100
  if dist>1.0: return None

  # FILTER 2: Pin Bar - 2.5x body (strong)
  o,h,l,c=last['open'],last['high'],last['low'],last['close']
  body=abs(c-o); body=body if body!=0 else 0.0001
  upper=h-max(o,c); lower=min(o,c)-l
  is_bull_pin = lower > 2.5*body
  is_bear_pin = upper > 2.5*body
  if not (is_bull_pin or is_bear_pin): return None

  # FILTER 3: RSI
  rsi=calc_rsi(closes_list)

  signal=None
  confidence=0

  # BUY LOGIC - will show BUY when pin is bullish
  if is_bull_pin:
   signal="BUY"
   if price>ema: confidence+=40 # with trend
   else: confidence+=15 # counter trend but still valid
   if rsi>50: confidence+=30
   if lower/body>3: confidence+=20
   if dist<0.5: confidence+=10

  # SELL LOGIC - will show SELL when pin is bearish
  if is_bear_pin:
   signal="SELL"
   if price<ema: confidence+=40
   else: confidence+=15
   if rsi<50: confidence+=30
   if upper/body>3: confidence+=20
   if dist<0.5: confidence+=10

  if confidence<55: return None # SKIP low quality = your profit filter

  return {"price":price,"ema":ema,"dist":dist,"signal":signal,"rsi":rsi,"conf":confidence,"high":h,"low":l}
 except Exception as e:
  print(e)
  return None

def fmt(p): return f"{p:.5f}"

send_telegram("🚀 *BIBLE PRO LIVE - 8 CURRENCIES*\nPairs: EURUSD GBPUSD USDCHF USDJPY USDCNH USDRUB AUDUSD NZDUSD\nFilters: Pin 2.5x + RSI + Confidence 55%+\nMode: BUY & SELL both")

while True:
 for name,ys in SYMBOLS.items():
  sig=get_pro_signal(ys)
  if sig:
   now=time.time()
   if name not in last_alert or now-last_alert[name]>14400: # 4h cooldown
    emoji="🟢" if sig['signal']=="BUY" else "🔴"
    sl = sig['low']*0.997 if sig['signal']=="BUY" else sig['high']*1.003
    tp1 = sig['price']*1.002 if sig['signal']=="BUY" else sig['price']*0.998
    tp2 = sig['price']*1.005 if sig['signal']=="BUY" else sig['price']*0.995

    msg=f"""{emoji} *{sig['signal']} {name}* - {sig['conf']}% Quality {emoji}

*Entry:* {fmt(sig['price'])}
*EMA21:* {fmt(sig['ema'])} ({sig['dist']:.2f}%)
*RSI:* {sig['rsi']:.1f}
*SL:* {fmt(sl)}
*TP1:* {fmt(tp1)}
*TP2:* {fmt(tp2)}

_Reason: D1 Pin Bar + RSI + Near EMA21_
_Time: {datetime.now().strftime('%d %b %H:%M')} EAT_"""
    send_telegram(msg)
    last_alert[name]=now
  time.sleep(2)
 time.sleep(180)
