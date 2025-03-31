from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from urllib.parse import urlparse

app = Flask(__name__)

# Sadece batuhandurmaz.com'dan gelen istekleri kabul et
CORS(app, origins=["https://www.batuhandurmaz.com"], methods=["POST", "OPTIONS"], allow_headers=["Content-Type"])

# Ortam değişkenleri
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Arama fonksiyonu
def search_internal_links(keyword, target_page, num_results=10):
    parsed_url = urlparse(target_page)
    domain = parsed_url.netloc  # örnek: www.siteniz.com

    # Sorgu: domainde keyword geçen ama hedef URL olmayan sayfalar
    query = f'site:{domain} "{keyword}" -inurl:{target_page}'

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'num': num_results
    }
    response = requests.get(url, params=params)
    data = response.json()
    return [item['link'] for item in data.get('items', [])]

# API endpoint
@app.route("/api/search", methods=["POST"])
def handle_search():
    data = request.json
    keyword = data.get("keyword")
    target_page = data.get("url")

    if not keyword or not target_page:
        return jsonify({"error": "Anahtar kelime ve hedef URL gereklidir."}), 400

    try:
        results = search_internal_links(keyword, target_page)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Railway port ayarı
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
