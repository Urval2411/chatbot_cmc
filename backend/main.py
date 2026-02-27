import os
import chromadb
from chromadb.utils import embedding_functions
import anthropic
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "my_documents"
TOP_K_RESULTS = 3

# Use ChromaDB's built-in embedding function (no torch needed)
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

print("Connecting to ChromaDB...")
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn
)
print("ChromaDB connected ✅")

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
print("Claude connected ✅")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

def retrieve_chunks(question):
    results = collection.query(
        query_texts=[question],
        n_results=TOP_K_RESULTS,
        include=["documents", "metadatas"]
    )
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    return chunks, sources

def generate_answer(question, chunks, sources):
    context = ""
    for i, (chunk, source) in enumerate(zip(chunks, sources)):
        context += f"\n--- Source: {source} (Chunk {i+1}) ---\n{chunk}\n"

    prompt = f"""You are a helpful assistant. Answer the user's question 
based ONLY on the context provided below. If the answer is not found 
in the context, say "I couldn't find relevant information in the documents."

CONTEXT FROM DOCUMENTS:
{context}

USER QUESTION:
{question}

Provide a clear, concise and well-summarised answer. 
Mention which document(s) you found the answer in."""

    message = claude.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

@app.post("/chat")
async def chat(request: QuestionRequest):
    question = request.question
    chunks, sources = retrieve_chunks(question)
    answer = generate_answer(question, chunks, sources)
    return {"answer": answer, "sources": list(set(sources))}

@app.get("/")
async def root():
    return {"status": "RAG Chatbot backend is running ✅"}