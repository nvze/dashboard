from flask import Flask, render_template, jsonify
import yfinance as yf
import requests

# Inisialisasi Flask (Wajib bernama 'app' huruf kecil agar dibaca oleh Vercel)
app = Flask(__name__)

def get_macro_data():
    """
    Fungsi untuk mengambil data secara real-time dari berbagai sumber.
    Menggunakan yfinance (Yahoo Finance) untuk data pasar global, 
    dan public API untuk kurs mata uang.
    """
    try:
        # Daftar Ticker di Yahoo Finance:
        # GC=F       : Harga Emas (Gold Futures)
        # DX-Y.NYB   : DXY (US Dollar Index)
        # ^JKSE      : IHSG (Jakarta Composite Index)
        tickers = {
            "gold": "GC=F",
            "dxy": "DX-Y.NYB",
            "ihsg": "^JKSE"
        }
        
        results = {}
        
        # 1. Ambil data Emas, DXY, dan IHSG
        for key, ticker in tickers.items():
            try:
                data = yf.Ticker(ticker)
                # Menggunakan 'fast_info' jauh lebih ringan dan cepat dibanding 'history'
                price = data.fast_info['last_price']
                results[key] = round(price, 2)
            except Exception as e:
                print(f"Error mengambil data {key}: {e}")
                results[key] = 0.0 # Nilai default jika API Yahoo limit/error

        # 2. Ambil Kurs USD ke IDR
        try:
            ex_res = requests.get('https://open.er-api.com/v6/latest/USD', timeout=5).json()
            results['usd_idr'] = ex_res['rates']['IDR']
        except Exception as e:
            print(f"Error mengambil data kurs: {e}")
            results['usd_idr'] = 0.0

        # 3. Ambil Yield SBN 10 Tahun
        # Catatan: Ticker obligasi negara sering dibatasi di public API gratis.
        # Jika Anda memiliki API key TradingEconomics, Anda bisa memasukkannya di sini.
        # Sementara ini menggunakan nilai statis/proxy terakhir.
        results['sbn10y'] = 6.85 

        return results

    except Exception as e:
        print(f"Terjadi kesalahan sistem: {e}")
        return None

# Rute Utama (Halaman Depan)
@app.route('/')
def index():
    # Vercel akan otomatis mencari file index.html di dalam folder 'templates'
    return render_template('index.html')

# Rute API (Untuk menyuplai data JSON ke Frontend secara real-time)
@app.route('/api/data')
def api_data():
    data = get_macro_data()
    if data:
        # Mengirimkan data dalam format JSON yang mudah dibaca JavaScript
        return jsonify(data)
    
    # Memberikan status error 500 jika gagal total
    return jsonify({"error": "Gagal mengambil data dari server"}), 500

# Blok ini hanya dieksekusi jika dijalankan secara lokal di laptop
if __name__ == '__main__':
    app.run(debug=True, port=5000)