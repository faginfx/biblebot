import time, requests, os
from flask import Flask
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SYMBOLS = {"EURUSD": "EURUSD=X", "GOLD": "GC=F", "BTC": "BTC-USD"}

app = Flask(__name__)
@app.route('/')
def home():
    return "BIBLE BOT 24/7 LIVE - FIXED 429"

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print(e)

def get_closes(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=15m&range=5d"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()
        closes = data['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]
        return closes
    except Exception as e:
        print(f"Fetch error {ticker}: {e}")
        return []

def ema(prices, period):
    if len(prices) < period: return 0
    k = 2/(period+1)
    ema_val = sum(prices[:period])/period
    for p in prices[period:]:
        ema_val = p*k + ema_val*(1-k)
    return ema_val

def scan():
    send("✅ BIBLE BOT 24/7 IS LIVE! Fixed 429 error\nWatching EURUSD + GOLD + BTC\nScanning every 2 mins")
    while True:
        for name, ticker in SYMBOLS.items():
            closes = get_closes(ticker)
            if len(closes) < 30:
                print(f"{name} not enough data {len(closes)}")
                time.sleep(5)
                continue

            price = closes[-1]
            ema21 = ema(closes, 21)
            ema8 = ema(closes, 8)
            dist = abs(price-ema21)/price*100

            print(f"{name} Price:{price:.4f} EMA21:{ema21:.4f} Dist:{dist:.2f}%")

            if dist < 0.6:
                if price > ema21 and ema8 > ema21:
                    send(f"🚀 BIBLE BUY SIGNAL: {name}\nPrice: {price}\nEMA21: {ema21:.2f}\nDist: {dist:.2f}% to EMA21\nStrategy: Page 98 Pin")
                elif price < ema21 and ema8 < ema21:
                    send(f"🔻 BIBLE SELL SIGNAL: {name}\nPrice: {price}\nEMA21: {ema21:.2f}\nDist: {dist:.2f}% to EMA21\nStrategy: Page 98 Pin")
            time.sleep(10)
        time.sleep(120)

threading.Thread(target=scan, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
