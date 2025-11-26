import os
import json
import yaml
import tempfile
import shutil
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename


from langchain_community.llms import Ollama
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains.retrieval_qa.base import RetrievalQA  # This should be exchanged as it security support will deprecate with December 2026
from langchain_core.documents import Document

from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader

app = Flask(__name__)

# Configuration 
MODEL_NAME = "granite4:350m"
EMBEDDING_MODEL = "nomic-embed-text"
VECTOR_STORE_PATH = "./chroma_db"
UPLOAD_FOLDER = "./temp_uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
vector_store = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
llm = OllamaLLM(model=MODEL_NAME)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

def load_and_process_file(file_path, file_ext):
    documents = []
    
    try:
        if file_ext == '.pdf':
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
        elif file_ext == '.csv':
            loader = CSVLoader(file_path)
            documents = loader.load()
            
        elif file_ext in ['.txt', '.md', '.eml', '.log']: 
            loader = TextLoader(file_path)
            documents = loader.load()
            
        elif file_ext in ['.json', '.jsonl', '.yaml', '.yml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_ext == '.json':
                    data = json.load(f)
                    text_content = json.dumps(data, indent=2)
                elif file_ext == '.jsonl':
                    data = [json.loads(line) for line in f]
                    text_content = json.dumps(data, indent=2)
                elif file_ext in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                    text_content = yaml.dump(data, sort_keys=False)
            
            documents = [Document(page_content=text_content, metadata={"source": file_path})]

        else:
            return None #

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

    return documents


@app.route('/ingest', methods=['POST'])
def ingest_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()
    
    temp_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(temp_path)

    raw_docs = load_and_process_file(temp_path, file_ext)

    if raw_docs is None:
        os.remove(temp_path) # Clean up
        return jsonify({"error": f"Unsupported file type or processing error: {file_ext}"}), 400

    for doc in raw_docs:
        doc.metadata["source"] = filename

    chunks = text_splitter.split_documents(raw_docs)
    vector_store.add_documents(chunks)
    os.remove(temp_path)

    return jsonify({
        "message": "File ingested successfully",
        "filename": filename,
        "chunks_created": len(chunks)
    })

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({"error": "No question provided"}), 400

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)
    
    response = qa_chain.invoke({"query": question})

    return jsonify({
        "answer": response['result'],
        "sources": list(set([doc.metadata.get('source') for doc in response['source_documents']]))
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)