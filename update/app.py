from flask import Flask, render_template, jsonify
import yfinance as yf
import requests

app = Flask(__name__)

def get_macro_data():
    try:
        # Ticker: DXY (US Dollar Index), ^JKSE (IHSG), IDN10Y.BD (SBN 10TH - Estimasi)
        tickers = {
            "dxy": "DX-Y.NYB",
            "ihsg": "^JKSE",
            "gold": "GC=F"
        }
        
        results = {}
        for key, ticker in tickers.items():
            data = yf.Ticker(ticker)
            price = data.fast_info['last_price']
            results[key] = round(price, 2)

        # Ambil Kurs USD/IDR dari API publik
        ex_res = requests.get('https://open.er-api.com/v6/latest/USD').json()
        results['usd_idr'] = ex_res['rates']['IDR']
        
        # Yield SBN 10Y (Contoh statis/scraping jika API tidak tersedia, 
        # di sini kita gunakan proksi dari Yahoo Finance jika tersedia)
        # Seringkali SBN 10Y menggunakan ticker khusus tergantung provider.
        results['sbn10y'] = 6.85 # Nilai benchmark rata-rata jika API sedang limit

        return results
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    data = get_macro_data()
    if data:
        return jsonify(data)
    return jsonify({"error": "Gagal mengambil data"}), 500

if __name__ == '__main__':
    # Gunakan debug=True untuk pengembangan
    app.run(debug=True, port=5000)