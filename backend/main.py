import os
import chromadb
from sentence_transformers import SentenceTransformer
import anthropic
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

# ── CONFIG ──────────────────────────────────────────────
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "my_documents"
TOP_K_RESULTS = 3
# ────────────────────────────────────────────────────────

# 1. Load embedding model
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded ✅")

# 2. Connect to ChromaDB
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(name=COLLECTION_NAME)
print("ChromaDB connected ✅")

# 3. Connect to Claude
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
print("Claude connected ✅")

# 4. Setup FastAPI
app = FastAPI()

# Allow React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Define request model
class QuestionRequest(BaseModel):
    question: str

# 6. Retrieval function
def retrieve_chunks(question):
    question_vector = model.encode(question).tolist()
    results = collection.query(
        query_embeddings=[question_vector],
        n_results=TOP_K_RESULTS,
        include=["documents", "metadatas"]
    )
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    return chunks, sources

# 7. Claude response function
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

# 8. Chat endpoint
@app.post("/chat")
async def chat(request: QuestionRequest):
    question = request.question
    print(f"\nQuestion received: {question}")

    chunks, sources = retrieve_chunks(question)
    print(f"Retrieved {len(chunks)} chunks from: {sources}")

    answer = generate_answer(question, chunks, sources)
    print(f"Answer generated ✅")

    return {
        "answer": answer,
        "sources": list(set(sources))
    }

# 9. Health check endpoint
@app.get("/")
async def root():
    return {"status": "RAG Chatbot backend is running ✅"}
