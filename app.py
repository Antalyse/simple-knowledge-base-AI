import os
# import json
# import yaml
# import tempfile
# import shutil
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from cli import UPLOAD_FOLDER, ingest, ask_question

# from langchain_community.llms import Ollama
# from langchain_ollama import OllamaEmbeddings, OllamaLLM
# from langchain_chroma import Chroma
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_classic.chains.retrieval_qa.base import RetrievalQA  # This should be exchanged as it security support will deprecate with December 2026
# from langchain_core.documents import Document

# from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader

app = Flask(__name__)

# # Configuration 
# MODEL_NAME = "granite4:350m"
# EMBEDDING_MODEL = "nomic-embed-text"
# VECTOR_STORE_PATH = "./chroma_db"
# UPLOAD_FOLDER = "./temp_uploads"

# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
# vector_store = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
# llm = OllamaLLM(model=MODEL_NAME)
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)



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
    
    ingest(temp_path)
    
    return jsonify({"message": "Files successfully ingested."}), 200
    

@app.route('/ask', methods=['POST'])
def route_ask():
    data = request.json
    question = data.get('question')
    model = data.get('model')
    k = data.get('k')

    if not question:
        return jsonify({"error": "No question provided"}), 400

    output, code = ask_question(question=question, model=model, k=k)

    return jsonify(output), code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)