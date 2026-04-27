import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from config import GROQ_API_KEY

CHROMA_DIR = "./chroma_db"

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_llm():
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile",
        temperature=0.1
    )

def ingest_document(file_path: str, doc_id: str) -> int:
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)

    embeddings = get_embeddings()
    vectorstore = Chroma(
        collection_name=doc_id,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )
    vectorstore.add_documents(chunks)

    return len(chunks)


def query_document(doc_id: str, question: str, chat_history: list = []) -> str:
    embeddings = get_embeddings()
    vectorstore = Chroma(
        collection_name=doc_id,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    # Find top 3 relevant chunks
    results = vectorstore.similarity_search(question, k=3)
    context = "\n\n".join([r.page_content for r in results])

    # Build prompt
    history_text = ""
    if chat_history:
        for msg in chat_history[-5:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

    prompt = f"""You are a helpful assistant that answers questions based on the provided document context.

Document Context:
{context}

{f"Previous conversation:{chr(10)}{history_text}" if history_text else ""}

Question: {question}

Answer based on the document context above. Be concise and helpful."""

    # Get answer from Groq
    llm = get_llm()
    response = llm.invoke(prompt)

    return response.content