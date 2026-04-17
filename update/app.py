from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Default market diatur ke "global" agar bisa mendeteksi hampir semua ticker
def fetch_tradingview_data(ticker, market="global"):
    """ 
    Fungsi universal untuk mengambil data dari API Scanner TradingView.
    """
    url = f"https://scanner.tradingview.com/{market}/scan"
    payload = {
        "symbols": {"tickers": [ticker]},
        "columns": ["close"] # Mengambil harga penutupan (current price/spot)
    }
    try:
        res = requests.post(url, json=payload, timeout=5)
        data = res.json()
        
        # Jika data kosong (ticker tidak ditemukan di market tersebut)
        if not data.get('data'):
            return 0.0
            
        value = data['data'][0]['d'][0]
        return value
    except Exception as e:
        print(f"Error fetching {ticker} dari TradingView: {e}")
        return 0.0

def get_macro_data():
    results = {}
    
    # 1. Emas Dunia - Dicari di pasar "global"
    results['gold'] = round(fetch_tradingview_data("OANDA:XAUUSD", "global"), 2)

    # 2. DXY (US Dollar Index) - Dicari di pasar "global"
    results['dxy'] = round(fetch_tradingview_data("TVC:DXY", "global"), 2)

    # 3. IHSG (Jakarta Composite Index) - KHUSUS dicari di pasar "indonesia"
    results['ihsg'] = round(fetch_tradingview_data("IDX:COMPOSITE", "indonesia"), 2)

    # 4. Kurs USD/IDR - Dicari di pasar "global"
    results['usd_idr'] = round(fetch_tradingview_data("FX_IDC:USDIDR", "global"), 2)

    # 5. Yield SBN 10 Tahun - Dicari di pasar "global"
    results['sbn10y'] = round(fetch_tradingview_data("TVC:ID10Y", "global"), 3)

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