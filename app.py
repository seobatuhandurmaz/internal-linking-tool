from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import pandas as pd

# Flask uygulaması
app = Flask(__name__)

# CORS sadece senin sitene açık
CORS(app, origins=["https://www.batuhandurmaz.com"])

# Ortam değişkenlerinden API key ve CSE ID alınıyor
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Google araması yapan fonksiyon
def search_google(query, num_results=10):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'num': num_results
    }
    response = requests.get(url, params=params)
    data = response.json()
    return [item['link'] for item in data.get("items", [])]

# CSV upload endpoint
@app.route("/api/upload-csv", methods=["POST"])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "CSV dosyası gönderilmedi"}), 400

    file = request.files['file']
    try:
        # CSV'yi oku
        df = pd.read_csv(file)

        # Gerekli sütunlar var mı kontrol et
        if 'keyword' not in df.columns or 'target_page' not in df.columns:
            return jsonify({"error": "CSV içinde 'keyword' ve 'target_page' sütunları olmalı"}), 400

        # Sonuçları tutacağımız liste
        result_data = []

        # Her satır için işlem yap
        for index, row in df.iterrows():
            keyword = row['keyword']
            target = row['target_page']
            query = f"site:{target} {keyword} -inurl:{target}"

            links = search_google(query)

            result_data.append({
                "keyword": keyword,
                "target_page": target,
                "results": links
            })

        # JSON olarak döndür
        return jsonify(result_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Railway için port dinlemesi
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
