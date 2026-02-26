import os
import fitz  # PyMuPDF
import chromadb
from sentence_transformers import SentenceTransformer

# ── CONFIG ──────────────────────────────────────────────
DOCS_FOLDER = "../documents"        
CHROMA_PATH = "./chroma_db"         
COLLECTION_NAME = "my_documents"
CHUNK_SIZE = 400                    
CHUNK_OVERLAP = 50                  
# ────────────────────────────────────────────────────────

# 1. Load embedding model
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded ✅")

# 2. Extract text from a single PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

# 3. Split text into overlapping chunks
def split_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

# 4. Setup ChromaDB
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)
print("ChromaDB ready ✅")

# 5. Process each PDF
all_chunks = []
all_ids = []
all_metadata = []

pdf_files = [f for f in os.listdir(DOCS_FOLDER) if f.endswith(".pdf")]
print(f"\nFound {len(pdf_files)} PDF(s): {pdf_files}\n")

for pdf_file in pdf_files:
    pdf_path = os.path.join(DOCS_FOLDER, pdf_file)
    print(f"Processing: {pdf_file}")

    raw_text = extract_text_from_pdf(pdf_path)
    chunks = split_into_chunks(raw_text)

    print(f"  → Extracted {len(chunks)} chunks")

    for i, chunk in enumerate(chunks):
        chunk_id = f"{pdf_file}_chunk_{i}"
        all_chunks.append(chunk)
        all_ids.append(chunk_id)
        all_metadata.append({"source": pdf_file, "chunk_index": i})

# 6. Generate embeddings
print(f"\nGenerating embeddings for {len(all_chunks)} total chunks...")
embeddings = model.encode(all_chunks, show_progress_bar=True).tolist()

# 7. Save to ChromaDB
collection.add(
    documents=all_chunks,
    embeddings=embeddings,
    ids=all_ids,
    metadatas=all_metadata
)

print(f"\n✅ Done! {len(all_chunks)} chunks saved to ChromaDB")
print(f"   Location: {CHROMA_PATH}")
print(f"   Collection: {COLLECTION_NAME}")