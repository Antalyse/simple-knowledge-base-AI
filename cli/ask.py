from typing import Tuple
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_classic.chains.retrieval_qa.base import RetrievalQA  # This should be exchanged as it security support will deprecate with December 2026


from .config import ASK_MODEL_NAME, ASK_K, VECTOR_STORE_PATH, EMBEDDING_MODEL

def ask_question(question: str, model: str = None, k: int = None) -> Tuple[dict, int]:
    llm = OllamaLLM(model=ASK_MODEL_NAME if not model else model)
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vector_store = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=embeddings)
    
    
    if not question:
        return {"error": "No question provided"}, 400

    retriever = vector_store.as_retriever(search_kwargs={"k": ASK_K if not k else k})
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)
    
    response = qa_chain.invoke({"query": question})
    
    output = {
        "answer": response['result'],
        "sources": list(set([doc.metadata.get('source') for doc in response['source_documents']]))
    }
    
    
    return output, 200