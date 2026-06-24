import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from utils.config import CHROMA_PERSIST_DIR, EMBEDDING_MODEL, GOOGLE_API_KEY
from utils.helpers import get_logger

logger = get_logger(__name__)

_embeddings = None
_vectorstore = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        logger.info("Loading Google Generative AI embeddings...")
        _embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY,
        )
    return _embeddings


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        _vectorstore = Chroma(
            collection_name="rag_documents",
            embedding_function=get_embeddings(),
            persist_directory=CHROMA_PERSIST_DIR,
        )
        logger.info("ChromaDB vectorstore loaded.")
    return _vectorstore


def reset_vectorstore():
    global _vectorstore
    _vectorstore = None
