from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def fetch_yahoo_data(ticker):
    """
    Fungsi untuk mengambil data langsung dari API Yahoo Finance.
    Kita menggunakan header 'User-Agent' untuk menyamar sebagai browser
    agar tidak diblokir oleh server Yahoo.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    # Endpoint API resmi Yahoo Finance untuk chart 1 hari
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        data = res.json()
        # Mengambil harga pasar reguler terbaru dari JSON yang dikembalikan Yahoo
        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        return round(price, 2)
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return 0.0

def get_macro_data():
    results = {}
    
    # 1. Ambil data Emas, DXY, dan IHSG menggunakan fungsi penyamaran
    results['gold'] = fetch_yahoo_data("GC=F")
    results['dxy'] = fetch_yahoo_data("DX-Y.NYB")
    results['ihsg'] = fetch_yahoo_data("^JKSE")

    # 2. Ambil Kurs USD ke IDR (Ini sudah terbukti berhasil di Vercel)
    try:
        ex_res = requests.get('https://open.er-api.com/v6/latest/USD', timeout=5).json()
        results['usd_idr'] = ex_res['rates']['IDR']
    except:
        results['usd_idr'] = 0.0

    # 3. Yield SBN 10 Tahun (Data Statis/Benchmark)
    results['sbn10y'] = 6.85 

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