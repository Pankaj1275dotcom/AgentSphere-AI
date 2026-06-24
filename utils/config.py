import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

GEMINI_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "models/gemini-embedding-001"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

CHROMA_PERSIST_DIR = "chroma_db"
BM25_INDEX_PATH = "data/bm25_index.pkl"
UPLOADS_DIR = "uploads"
DATA_DIR = "data"

TOP_K_RETRIEVAL = 5
TOP_K_FINAL = 4