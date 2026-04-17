from flask import Flask, render_template, jsonify
import yfinance as yf
import requests

app = Flask(__name__)

def get_macro_data():
    try:
        # Ticker Yahoo Finance: Emas (GC=F), DXY (DX-Y.NYB), IHSG (^JKSE)
        tickers = {
            "gold": "GC=F",
            "dxy": "DX-Y.NYB",
            "ihsg": "^JKSE"
        }
        
        results = {}
        
        # 1. Ambil Data Pasar Global
        for key, ticker in tickers.items():
            try:
                data = yf.Ticker(ticker)
                price = data.fast_info['last_price']
                results[key] = round(price, 2)
            except:
                results[key] = 0.0

        # 2. Ambil Kurs USD ke IDR
        try:
            ex_res = requests.get('https://open.er-api.com/v6/latest/USD', timeout=5).json()
            results['usd_idr'] = ex_res['rates']['IDR']
        except:
            results['usd_idr'] = 0.0

        # 3. Yield SBN 10 Tahun (Nilai estimasi/statis sebagai benchmark)
        results['sbn10y'] = 6.85 

        return results
    except Exception as e:
        print(f"Error: {e}")
        return None

# Rute Utama disesuaikan untuk /update
@app.route('/update')
@app.route('/update/')
def index():
    return render_template('index.html')

# Rute API disesuaikan untuk /update/api/data
@app.route('/update/api/data')
def api_data():
    data = get_macro_data()
    if data:
        return jsonify(data)
    return jsonify({"error": "Gagal mengambil data"}), 500

if __name__ == '__main__':
    app.run(debug=True)