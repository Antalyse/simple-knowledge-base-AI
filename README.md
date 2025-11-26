# Simple Knowledge Base AI
Simple Knowledge Base AI is a lightweight, local RAG API (Flask + Ollama + LangChain).

It provides a simple, privacy-focused **Retrieval-Augmented Generation (RAG)** API that allows you to "chat" with your own documents and data sources without sending sensitive information to a cloud service. It leverages **Ollama** to run Large Language Models (LLMs) locally, **LangChain** for orchestration, and **ChromaDB** as the vector store for persistent memory.

## 🌟 Features

* **Local Execution:** Runs entirely on your machine using your installed Ollama models.
* **Persistent Memory:** Data is saved locally in the `./chroma_db` directory, surviving server restarts.
* **Diverse File Support:** Ingests files like PDF, TXT, CSV, JSON, YAML, and EML.
* **Simple API:** Two straightforward endpoints for data ingestion and querying.

## 🛠️ Prerequisites

1.  **System Requirements** Using below mentioned models requires certain hardware resources. 
    * CPU: min. 2 Cores (degraded output quality). recommending 4+ cores
    * RAM: Using Ubuntu 24.04 LTS 64-Bit it required a total of 1.6 GB RAM


1.  **Ollama:** Must be installed and running on your system.
    * Pull the recommended models for generation and embeddings:
        ```bash
        ollama pull granite4:350m       # For answering questions (Generation Model)
        ollama pull nomic-embed-text    # For creating vector embeddings (Embedding Model)
        ```
2.  **Python:** Python 3.9+ environment.

---

## 💻 Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Antalyse/simple-knowledge-base-AI.git ./simpleKnowledgeBaseAI
    cd simpleKnowledgeBaseAI
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Ensure `app.py` is configured** with your chosen Ollama models (default is `granite4:350m` and `nomic-embed-text`).

---

## ▶️ Running the API

Start the server using Flask:

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

---

## 🚀 API Endpoints

### 1. Ingest Data

* **Endpoint:** `POST /ingest`
* **Purpose:** Uploads a file, processes it, splits it into chunks, embeds those chunks, and stores them in the ChromaDB vector store.
* **Method:** `multipart/form-data` (requires a file upload).
* **Supported File Types:** `.pdf`, `.txt`, `.csv`, `.json`, `.jsonl`, `.yaml`, `.yml`, and `.eml`.

#### Example: Uploading a PDF Document

```bash
curl -X POST http://localhost:5000/ingest \
  -F "file=@/path/to/my_software_documentation.pdf"
```

#### Example: Uploading a Structured JSON File

```bash
curl -X POST http://localhost:5000/ingest \
  -F "file=@/path/to/file_tree.json"
```

### 2. Ask a Question

* **Endpoint:** `POST /ask`
* **Purpose:** Takes a question, finds the 3 most relevant data chunks in the vector store, feeds them and the question to the local LLM (`llama3.2`), and returns a contextual answer.
* **Method:** `application/json`

#### Example: Querying the Ingested Data

```bash
curl -X POST http://localhost:5000/ask \
     -H "Content-Type: application/json" \
     -d '{ "question": "What is the main function of the app.py file according to the documentation?" }'
```

#### Example Response

```json
{
  "answer": "The main function of the app.py file is to initialize the Flask server and define the ingestion and query endpoints.",
  "sources": [
    "my_software_documentation.pdf",
    "file_tree.json"
  ]
}
```

---

## ⚙️ Core Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **API** | Flask | Provides the simple HTTP interface. |
| **Orchestrator** | LangChain | Connects LLM, Embeddings, and Vector Store (RAG pipeline). |
| **LLM Provider** | Ollama | Runs the LLM (e.g., Granite 4) entirely locally. |
| **Vector Store** | ChromaDB | Stores text chunks and their embeddings on disk. |
| **Embeddings** | OllamaEmbeddings (nomic-embed-text) | Converts text data into numerical vectors for searching. |