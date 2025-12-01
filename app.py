import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import ollama
from cli.config import ASK_K, UPLOAD_FOLDER, FILE_TYPES
from cli.ingest import ingest
from cli.ask import ask_question


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():    
    return render_template('index.html', file_types=",".join(FILE_TYPES), ask_k=ASK_K)

@app.route('/models', methods=['GET'])
def models():
    models_info = ollama.list()
    output = []
    for model in models_info['models']:
        output.append(model['model'])
    return jsonify({"models": output}), 200


@app.route('/ingest', methods=['POST'])
def route_ingest():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    
    temp_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(temp_path)
    output, code = ingest(temp_path)
    
    return jsonify(output), code
    

@app.route('/ask', methods=['POST'])
def route_ask():
    data = request.json
    question = data.get('question')
    model = data.get('model')
    k = int(data.get('k'))

    if not question:
        return jsonify({"error": "No question provided"}), 400

    output, code = ask_question(question=question, model=model, k=k)

    return jsonify(output), code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)