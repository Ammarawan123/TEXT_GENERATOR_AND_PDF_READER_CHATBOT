from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from PyPDF2 import PdfReader
from flask_caching import Cache
import os
import re
import time

# Flask app configuration
app = Flask(__name__)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # Cache timeout in seconds
app.config['UPLOAD_FOLDER'] = './uploads'  # Folder to store uploaded PDFs
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
cache = Cache(app)

# Configure Generative AI API
genai.configure(api_key="AIzaSyDvjQzvRZ8rx9_2Gt-EUMP6YiFbM6VvfJA")  # Replace with your actual API key
model = genai.GenerativeModel("gemini-1.5-flash")

# Extract text from the PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Filter relevant content using keywords
def filter_relevant_text(full_text, query, context_window=3000):
    keywords = re.escape(query)
    pattern = re.compile(f".{{0,{context_window}}}{keywords}.{{0,{context_window}}}", re.IGNORECASE)
    matches = pattern.findall(full_text)
    return " ".join(matches) if matches else full_text[:context_window]

# Retry mechanism for handling rate limits
def generate_with_retries(prompt, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            if "Resource has been exhausted" in str(e) and attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))
            else:
                raise e

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    return jsonify({"message": "File uploaded successfully", "file_path": file_path})

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        user_input = request.json.get('question')
        file_path = request.json.get('file_path')

        if not user_input:
            return jsonify({"error": "No question provided"}), 400

        cached_response = cache.get((user_input, file_path))
        if cached_response:
            return jsonify({"response": cached_response})

        # Load the PDF content
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        full_pdf_content = extract_text_from_pdf(file_path)
        relevant_content = filter_relevant_text(full_pdf_content, user_input)

        # Create the prompt
        prompt = f"Using the following content, answer the question:\n{relevant_content}\n\nQuestion: {user_input}"
        response = generate_with_retries(prompt)

        cache.set((user_input, file_path), response.text)

        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
