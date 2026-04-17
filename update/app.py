from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def fetch_tradingview_data(ticker, market="global"):
    """ 
    Fungsi universal untuk mengambil data dari API Scanner TradingView.
    Parameter 'market' ditambahkan agar bisa mengambil IHSG dari pasar Indonesia.
    """
    url = f"https://scanner.tradingview.com/{market}/scan"
    payload = {
        "symbols": {"tickers": [ticker]},
        "columns": ["close"] # Mengambil harga penutupan (current price/spot)
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
    
    # 1. Emas Dunia (XAU/USD Spot) - Menggunakan data OANDA yang sangat real-time
    results['gold'] = round(fetch_tradingview_data("OANDA:XAUUSD", "forex"), 2)

    # 2. DXY (US Dollar Index)
    results['dxy'] = round(fetch_tradingview_data("TVC:DXY", "cfd"), 2)

    # 3. IHSG (Jakarta Composite Index) - Harus diarahkan ke market 'indonesia'
    results['ihsg'] = round(fetch_tradingview_data("IDX:COMPOSITE", "indonesia"), 2)

    # 4. Kurs USD/IDR (Spot Rate)
    results['usd_idr'] = round(fetch_tradingview_data("FX_IDC:USDIDR", "forex"), 2)

    # 5. Yield SBN 10 Tahun (Indonesia 10Y Bond)
    results['sbn10y'] = round(fetch_tradingview_data("TVC:ID10Y", "cfd"), 3)

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