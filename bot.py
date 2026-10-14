import yfinance as yf, time, requests, os
from flask import Flask
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SYMBOLS = {"EURUSD": "EURUSD=X", "GOLD": "GC=F", "BTC": "BTC-USD"}

app = Flask(__name__)
@app.route('/')
def home():
    return "BIBLE BOT 24/7 LIVE"

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print(e)

def scan():
    send("✅ BIBLE BOT 24/7 IS LIVE! Watching EURUSD + GOLD + BTC\nFixed GOLD symbol - scanning every 60s")
    while True:
        for name, ticker in SYMBOLS.items():
            try:
                df = yf.download(ticker, period="2d", interval="15m", progress=False, auto_adjust=True)
                if len(df) < 25: 
                    print(f"{name} no data")
                    continue
                df['EMA21'] = df['Close'].ewm(span=21).mean()
                df['EMA8'] = df['Close'].ewm(span=8).mean()
                last = df.iloc[-1]
                price = float(last['Close'])
                ema21 = float(last['EMA21'])
                dist = abs(price-ema21)/price*100
                print(f"{name} {price:.2f} EMA21 {ema21:.2f} dist {dist:.2f}%")
                if dist < 0.5:
                    if price > ema21:
                        send(f"🚀 {name} BUY setup near EMA21\nPrice: {price}\nDist: {dist:.2f}% - Page 98 Pin")
                    else:
                        send(f"🔻 {name} SELL setup near EMA21\nPrice: {price}\nDist: {dist:.2f}% - Page 98 Pin")
            except Exception as e:
                print(f"Error {name}: {e}")
        time.sleep(60)

threading.Thread(target=scan, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
