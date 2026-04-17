from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def fetch_yahoo_data(ticker):
    """ Mengambil data Emas, DXY, dan IHSG dengan bypass blokir Yahoo """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        data = res.json()
        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        return round(price, 2)
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return 0.0

def fetch_tradingview_data(ticker):
    """ 
    Fungsi universal untuk mengambil data langsung dari API TradingView.
    Bisa digunakan untuk Obligasi (TVC) maupun Forex (FX_IDC).
    """
    url = "https://scanner.tradingview.com/global/scan"
    payload = {
        "symbols": {"tickers": [ticker]},
        "columns": ["close"] # Mengambil harga penutupan (current price)
    }
    try:
        res = requests.post(url, json=payload, timeout=5)
        data = res.json()
        value = data['data'][0]['d'][0]
        return value
    except Exception as e:
        print(f"Error fetching {ticker} dari TradingView: {e}")
        return 0.0

def get_macro_data():
    results = {}
    
    # 1. Ambil data Emas, DXY, dan IHSG dari Yahoo Finance
    results['gold'] = fetch_yahoo_data("GC=F")
    results['dxy'] = fetch_yahoo_data("DX-Y.NYB")
    results['ihsg'] = fetch_yahoo_data("^JKSE")

    # 2. Ambil Kurs USD/IDR dan Yield SBN 10 Tahun dari TradingView
    # Menggunakan round untuk membatasi jumlah desimal
    results['usd_idr'] = round(fetch_tradingview_data("FX_IDC:USDIDR"), 2)
    results['sbn10y'] = round(fetch_tradingview_data("TVC:ID10Y"), 3)

    return results

# Rute Utama
@app.route('/update')
@app.route('/update/')
def index():
    return render_template('index.html')

# Rute API
@app.route('/update/api/data')
def api_data():
    data = get_macro_data()
    if data:
        return jsonify(data)
    return jsonify({"error": "Gagal mengambil data"}), 500

if __name__ == '__main__':
    app.run(debug=True)