import os 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader
from langchain_core.documents import Document
from langchain_chroma import Chroma

import yaml
import json

from .config import VECTOR_STORE_PATH, EMBEDDING_MODEL

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
            return None

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

    return documents


def ingest_file(filename: str):
    
    file_path = os.path.splitext(filename)[0]
    file_ext = os.path.splitext(filename)[1].lower()
    
    raw_docs = load_and_process_file(filename, file_ext)

    if raw_docs is None:
        return {"error": f"Unsupported file type or processing error: {file_ext}"}, 400

    for doc in raw_docs:
        doc.metadata["source"] = filename
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(raw_docs)
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vector_store = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
    vector_store.add_documents(chunks)

    output = {
        "message": "File ingested successfully",
        "filename": filename,
        "chunks_created": len(chunks)
    }

    print(f"{output['message']}: {output['filename']}")



    return output, 200


def ingest(path):
    if path == ".":
        path = os.getcwd()
    
    if path == "..":
        print(".. not allowed.")
        return "Command not allowed", 400
    
    if os.path.isdir(path):
        path = path + "/" if not path.endswith("/") else path
    
    if os.path.isdir(path):
        files = os.listdir(path)
        outputs = []
        for filepath in files:
            if not os.path.isdir(path + filepath):
                output, code = ingest_file(path + filepath)
                outputs += [json.dumps(output)]
        output = "\n".join(outputs)
    
    else:
        output = ingest_file(path)
        
        
    return output, 200