from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)


MONGO_URI = os.environ.get("MONGO_URI") or "your_mongodb_connection_string"
client = MongoClient(MONGO_URI)
db = client["chatbot"]          
collection = db["EDU"]          


data = list(collection.find({}, {"_id": 0, "question": 1, "category": 1}))
questions = [item["question"] for item in data]


vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(questions)

@app.route("/predict", methods=["POST"])
def predict():
    user_text = request.json.get("message", "") 
    if not user_text:
        return jsonify({"error": "يرجى إدخال سؤال."}), 400


    
    user_vector = vectorizer.transform([user_text])
    similarities = cosine_similarity(user_vector, tfidf_matrix)
    best_match_index = similarities.argmax()
    best_score = similarities[0][best_match_index]

   
    if best_score < 0.4:
        return jsonify({"error": "عذرًا، لم أتمكن من فهم سؤالك. حاول صياغته بطريقة مختلفة."}), 404

    best_item = data[best_match_index]
    return jsonify({
        "category": best_item.get("category", "general"),
        "question": best_item["question"],
        "similarity_score": float(best_score)
    })


if __name__ == "__main__":
    app.run(port=5000)
