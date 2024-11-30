import logging
import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_file_path = os.path.join(base_dir, 'logs', 'Apirag.log')

# Configure logging to write to a file
# Ensure the logs directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Clear existing handlers (if any) to avoid conflicts
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()  # Optional: Also log to console
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load SentenceTransformer model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# MongoDB setup
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['product-review-data1']
    collection = db['product_reviews7'] 
    client.admin.command('ping')  # Check MongoDB connection
    print("MongoDB connection successful")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    collection = None

# Groq API settings
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
#Ensure the key is stored securely in the environment
GROQ_API_KEY = os.getenv('GROQ_API_KEY')  

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

@app.route('/query', methods=['POST'])
def query():
    # Check if the request contains the required data
    query_text = request.json.get('query')
    if not query_text:
        return jsonify({"error": "Query not provided"}), 400
    print(f"Received query: {query_text}")

    # Ensure the SentenceTransformer model is available
    if not embedding_model:
        return jsonify({"error": "Embedding model not loaded"}), 500

    # Encode the query
    try:
        query_embedding = embedding_model.encode(query_text)
    except Exception as e:
        return jsonify({"error": "Failed to encode query", "details": str(e)}), 500

    # Ensure the MongoDB collection is available
    if collection is None:
        return jsonify({"error": "MongoDB collection not available"}), 500

    # Retrieve all reviews from the collection
    try:
        results = list(collection.find())
        if not results:
            return jsonify({"error": "No reviews found in the database"}), 404
    except Exception as e:
        return jsonify({"error": "Failed to fetch data from MongoDB", "details": str(e)}), 500

    # Calculate similarity between query and document embeddings
    similarities = []
    for result in results:
        try:
            similarity = np.dot(query_embedding, result['embeddings'])
            similarities.append((result, similarity))
        except KeyError as e:
            print(f"Key error: {e} in document: {result}")
        except Exception as e:
            print(f"Error calculating similarity: {e}")

    # Sort results by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Get the top 5 most similar reviews
    top_results = [result for result, _ in similarities[:5]]

    # Create a context string
    context = " ".join([
        f"Product: {result['product_name']} Review: {result['review_content']}"
        for result in top_results
    ])

    # Use Groq API for text generation
    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            },
            json={
                "model": "llama3-8b-8192",  
                "messages": [
                    {"role": "user", "content": query_text + "\n" + context}
                ]
            }
        )

        if response.status_code != 200:
            return jsonify({
                "error": "Failed to generate text",
                "details": response.json()
            }), response.status_code

        generated_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        return jsonify({ 
            "Query": query_text,
            "generated_text": generated_text})

    except Exception as e:
        return jsonify({"error": "Failed to connect to Groq API", "details": str(e)}), 500


if __name__ == "__main__":
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Error starting the Flask app: {e}")
