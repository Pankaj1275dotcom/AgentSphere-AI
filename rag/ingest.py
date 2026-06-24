import os
import pickle
import tempfile
from typing import List, Tuple

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from rag.vectorstore import get_vectorstore
from rag.hybrid import save_bm25_index, load_bm25_index, build_bm25_index
from utils.config import CHUNK_SIZE, CHUNK_OVERLAP, BM25_INDEX_PATH, DATA_DIR
from utils.helpers import compute_file_hash, ensure_dirs, get_logger

logger = get_logger(__name__)

_ingested_hashes: set = set()


def load_ingested_hashes() -> set:
    global _ingested_hashes
    hash_file = os.path.join(DATA_DIR, "ingested_hashes.pkl")
    if os.path.exists(hash_file):
        with open(hash_file, "rb") as f:
            _ingested_hashes = pickle.load(f)
    return _ingested_hashes


def save_ingested_hashes(hashes: set):
    ensure_dirs(DATA_DIR)
    hash_file = os.path.join(DATA_DIR, "ingested_hashes.pkl")
    with open(hash_file, "wb") as f:
        pickle.dump(hashes, f)


def is_duplicate(file_hash: str) -> bool:
    hashes = load_ingested_hashes()
    return file_hash in hashes


def ingest_pdf(file_bytes: bytes, filename: str) -> Tuple[bool, str, int]:
    """Ingest a PDF into ChromaDB and BM25 index. Returns (success, message, num_chunks)."""
    file_hash = compute_file_hash(file_bytes)

    if is_duplicate(file_hash):
        return False, f"'{filename}' was already indexed (duplicate detected).", 0

    ensure_dirs(DATA_DIR)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
    except Exception as e:
        logger.error(f"Failed to load PDF '{filename}': {e}")
        return False, f"Failed to load '{filename}': {e}", 0
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(pages)

    for chunk in chunks:
        chunk.metadata["source"] = filename
        chunk.metadata["file_hash"] = file_hash

    if not chunks:
        return False, f"No text could be extracted from '{filename}'.", 0

    vs = get_vectorstore()
    vs.add_documents(chunks)
    logger.info(f"Added {len(chunks)} chunks from '{filename}' to ChromaDB.")

    existing_docs = load_all_documents()
    bm25 = build_bm25_index(existing_docs)
    save_bm25_index(bm25, existing_docs)

    hashes = load_ingested_hashes()
    hashes.add(file_hash)
    save_ingested_hashes(hashes)

    return True, f"Successfully indexed '{filename}' ({len(chunks)} chunks).", len(chunks)


def load_all_documents() -> List[Document]:
    """Load all documents currently in the vectorstore."""
    try:
        vs = get_vectorstore()
        results = vs.get(include=["documents", "metadatas"])
        docs = []
        for text, meta in zip(results["documents"], results["metadatas"]):
            docs.append(Document(page_content=text, metadata=meta or {}))
        return docs
    except Exception as e:
        logger.error(f"Error loading all documents: {e}")
        return []


def get_indexed_stats() -> dict:
    """Return statistics about indexed documents."""
    try:
        vs = get_vectorstore()
        results = vs.get(include=["metadatas"])
        sources = set()
        for meta in results["metadatas"]:
            if meta and "source" in meta:
                sources.add(meta["source"])
        return {
            "total_chunks": len(results["metadatas"]),
            "total_documents": len(sources),
            "documents": sorted(sources),
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {"total_chunks": 0, "total_documents": 0, "documents": []}


def delete_indexed_document(source: str) -> Tuple[bool, str]:
    """Delete all chunks for the given indexed source document and rebuild search indexes."""
    try:
        vs = get_vectorstore()
        results = vs.get()
        ids_to_delete = [
            idx
            for idx, meta in zip(results["ids"], results["metadatas"])
            if meta and meta.get("source") == source
        ]

        if not ids_to_delete:
            return False, f"No indexed chunks found for '{source}'."

        vs.delete(ids=ids_to_delete)

        remaining_docs = load_all_documents()
        if remaining_docs:
            bm25 = build_bm25_index(remaining_docs)
            save_bm25_index(bm25, remaining_docs)
        else:
            if os.path.exists(BM25_INDEX_PATH):
                os.remove(BM25_INDEX_PATH)

        hashes = load_ingested_hashes()
        deleted_hashes = {
            meta.get("file_hash")
            for meta in results["metadatas"]
            if meta and meta.get("source") == source and meta.get("file_hash")
        }
        hashes = {h for h in hashes if h not in deleted_hashes}
        save_ingested_hashes(hashes)

        logger.info(f"Deleted indexed document '{source}' and rebuilt indexes.")
        return True, f"Deleted indexed document '{source}'."
    except Exception as e:
        logger.error(f"Failed to delete indexed document '{source}': {e}")
        return False, f"Failed to delete '{source}': {e}"
