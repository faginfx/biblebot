import yfinance as yf, time, requests, os
from flask import Flask
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8999513909:AAFX__8ZGJooONpMSaZ46wNMBaq12sPmw6g")
CHAT_ID = os.environ.get("CHAT_ID", "8307791583")
SYMBOLS = ["EURUSD=X", "XAUUSD=X", "BTC-USD"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def run_bot():
    send_telegram("✅ BIBLE BOT 24/7 IS LIVE! Watching EURUSD + GOLD + BTC")
    while True:
        try:
            for SYMBOL in SYMBOLS:
                df = yf.download(SYMBOL, period="5d", interval="15m", auto_adjust=True, progress=False)
                if len(df) < 30: continue
                df['EMA21'] = df['Close'].ewm(span=21).mean()
                df['EMA8'] = df['Close'].ewm(span=8).mean()
                last = df.iloc[-1]
                price = float(last['Close'])
                ema21 = float(last['EMA21']); ema8 = float(last['EMA8'])
                trend = "UPTREND" if ema8 > ema21 else "DOWNTREND"
                near = abs(price - ema21) / price < 0.003
                c=float(last['Close']); o=float(last['Open']); h=float(last['High']); l=float(last['Low'])
                body=abs(c-o)
                bull_pin = (min(c,o)-l) > 2.2*body if body>0 else False
                bear_pin = (h-max(c,o)) > 2.2*body if body>0 else False
                if trend=="UPTREND" and near and bull_pin:
                    send_telegram(f"🟢 BUY NOW {SYMBOL} @ {price}\n{trend} | Page98 HIGH PROB")
                elif trend=="DOWNTREND" and near and bear_pin:
                    send_telegram(f"🔴 SELL NOW {SYMBOL} @ {price}\n{trend} | Page98 HIGH PROB")
            time.sleep(60)
        except: time.sleep(60)

app = Flask(__name__)
@app.route('/')
def home(): return "BibleBot Alive"
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
