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

def fetch_tradingview_sbn():
    """ 
    Mengambil data SBN 10 Tahun (TVC:ID10Y) langsung dari API TradingView.
    Sangat akurat, real-time, dan persis seperti di web TradingView.
    """
    url = "https://scanner.tradingview.com/global/scan"
    payload = {
        "symbols": {"tickers": ["TVC:ID10Y"]},
        "columns": ["close"] # Kita hanya mengambil harga penutupan (yield terakhir)
    }
    try:
        res = requests.post(url, json=payload, timeout=5)
        data = res.json()
        # Menelusuri struktur JSON balasan TradingView untuk mendapatkan angkanya
        yield_value = data['data'][0]['d'][0]
        return round(yield_value, 3)
    except Exception as e:
        print(f"Error fetching TVC:ID10Y: {e}")
        return 0.0

def get_macro_data():
    results = {}
    
    # 1. Ambil data Emas, DXY, dan IHSG
    results['gold'] = fetch_yahoo_data("GC=F")
    results['dxy'] = fetch_yahoo_data("DX-Y.NYB")
    results['ihsg'] = fetch_yahoo_data("^JKSE")

    # 2. Ambil Kurs USD ke IDR
    try:
        ex_res = requests.get('https://open.er-api.com/v6/latest/USD', timeout=5).json()
        results['usd_idr'] = ex_res['rates']['IDR']
    except:
        results['usd_idr'] = 0.0

    # 3. Ambil Yield SBN 10 Tahun (Real-time TradingView)
    results['sbn10y'] = fetch_tradingview_sbn()

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