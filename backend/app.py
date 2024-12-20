from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import requests
from transformers import pipeline

app = Flask(__name__)
CORS(app)  # Enable CORS

# Initialize Hugging Face Summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Bing Search API Configuration
BING_API_KEY = "486e833cf02a48c1a0be8112c9655676"
BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"

# Search Bing
def search_bing(query):
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "textDecorations": True, "textFormat": "HTML"}
    response = requests.get(BING_ENDPOINT, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None

# Summarize Text
def summarize_text(text):
    try:
        summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        print("Summarization Error:", e)
        return text

# Home route (optional)
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the AI Chatbot Backend. Use the /query endpoint to interact."})

# Query route
@app.route('/query', methods=['GET', 'POST'])
def handle_query():
    if request.method == 'GET':
        return jsonify({"message": "Please send a POST request with a 'query' parameter."})

    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    search_results = search_bing(query)
    if search_results and "webPages" in search_results:
        snippets = " ".join([item["snippet"] for item in search_results["webPages"]["value"][:3]])
        summarized_answer = summarize_text(snippets)
        return jsonify({"answer": summarized_answer})
    else:
        return jsonify({"answer": "No relevant information found."})

@app.route('/test', methods=['GET'])
def test():
    return "Backend is running!"

if __name__ == '__main__':
    # Ensure Flask doesn't serve other files unintentionally
    app.run(debug=True, use_reloader=False)

