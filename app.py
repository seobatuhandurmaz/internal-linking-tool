from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)

# ❗ Sadece bu domaine izin veriyoruz:
CORS(app, origins=["https://www.batuhandurmaz.com"])

# Google API bilgilerimizi ortamdan alıyoruz
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Google Custom Search sorgusu
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
    links = [item['link'] for item in data.get("items", [])]
    return links

# API endpoint
@app.route("/api/search", methods=["POST"])
def keyword_search():
    data = request.json
    keyword = data.get("keyword")
    target_url = data.get("url")

    if not keyword or not target_url:
        return jsonify({"error": "Anahtar kelime ve hedef URL gereklidir."}), 400

    # Sorgu: hedef site dışında anahtar kelimeye dair rakip URL'ler
    query = f"{keyword} -site:{target_url}"

    try:
        links = search_google(query)
        return jsonify({"results": links})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Railway için port dinlemesi
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
