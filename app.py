from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

# Flask uygulaması başlat
app = Flask(__name__)

# Sadece bu domain'den gelen istekler kabul edilir
CORS(app, origins=["https://www.batuhandurmaz.com"], methods=["POST", "OPTIONS"], allow_headers=["Content-Type"])

# Google API bilgilerini ortam değişkeninden al
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Arama sorgusu yapan fonksiyon
def search_google_internal_links(keyword, url, num_results=10):
    query = f"site:{url} {keyword} -inurl:{url}"
    api_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "num": num_results
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    return [item["link"] for item in data.get("items", [])]

# API endpoint: /api/search
@app.route("/api/search", methods=["POST"])
def internal_link_suggestions():
    data = request.json
    keyword = data.get("keyword")
    url = data.get("url")

    if not keyword or not url:
        return jsonify({"error": "Anahtar kelime ve hedef URL gereklidir."}), 400

    try:
        results = search_google_internal_links(keyword, url)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Railway port ayarı
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
