from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import pandas as pd

# Flask uygulaması
app = Flask(__name__)

# ✅ CORS - Preflight sorunlarını çözmek için methods ve headers belirtildi
CORS(app, origins=["https://www.batuhandurmaz.com"], methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type"])

# Ortam değişkenlerinden API key ve CSE ID al
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

# CSV upload endpoint (JSON döner)
@app.route("/api/upload-csv", methods=["POST"])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "CSV dosyası gönderilmedi"}), 400

    file = request.files['file']
    try:
        df = pd.read_csv(file)

        if 'keyword' not in df.columns or 'target_page' not in df.columns:
            return jsonify({"error": "CSV içinde 'keyword' ve 'target_page' sütunları olmalı"}), 400

        result_data = []
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

        return jsonify(result_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Tekli sorgu için ek endpoint (isteğe bağlı)
@app.route("/api/search", methods=["POST"])
def keyword_search():
    data = request.json
    keyword = data.get("keyword")
    target_url = data.get("url")

    if not keyword or not target_url:
        return jsonify({"error": "Anahtar kelime ve hedef URL gereklidir."}), 400

    query = f"{keyword} -site:{target_url}"
    try:
        links = search_google(query)
        return jsonify({"results": links})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Railway port tanımı
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
