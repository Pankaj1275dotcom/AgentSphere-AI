import os
import pickle
from typing import List, Tuple

from rank_bm25 import BM25Okapi
from langchain_core.documents import Document

from utils.config import BM25_INDEX_PATH, DATA_DIR
from utils.helpers import ensure_dirs, get_logger

logger = get_logger(__name__)


def tokenize(text: str) -> List[str]:
    return text.lower().split()


def build_bm25_index(documents: List[Document]) -> BM25Okapi:
    corpus = [tokenize(doc.page_content) for doc in documents]
    return BM25Okapi(corpus)


def save_bm25_index(bm25: BM25Okapi, documents: List[Document]):
    ensure_dirs(DATA_DIR)
    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump({"bm25": bm25, "documents": documents}, f)
    logger.info(f"BM25 index saved ({len(documents)} docs).")


def load_bm25_index() -> Tuple[BM25Okapi | None, List[Document]]:
    if not os.path.exists(BM25_INDEX_PATH):
        return None, []
    try:
        with open(BM25_INDEX_PATH, "rb") as f:
            data = pickle.load(f)
        return data["bm25"], data["documents"]
    except Exception as e:
        logger.error(f"Failed to load BM25 index: {e}")
        return None, []


def bm25_search(query: str, top_k: int = 5) -> List[Document]:
    bm25, documents = load_bm25_index()
    if bm25 is None or not documents:
        return []
    tokens = tokenize(query)
    scores = bm25.get_scores(tokens)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [documents[i] for i in top_indices if scores[i] > 0]


def reciprocal_rank_fusion(
    semantic_docs: List[Document],
    bm25_docs: List[Document],
    k: int = 60,
    top_k: int = 4,
) -> List[Document]:
    """Combine semantic and BM25 results using Reciprocal Rank Fusion."""
    scores: dict = {}

    def doc_id(doc: Document) -> str:
        return doc.page_content[:100]

    doc_map: dict = {}

    for rank, doc in enumerate(semantic_docs):
        did = doc_id(doc)
        scores[did] = scores.get(did, 0) + 1.0 / (k + rank + 1)
        doc_map[did] = doc

    for rank, doc in enumerate(bm25_docs):
        did = doc_id(doc)
        scores[did] = scores.get(did, 0) + 1.0 / (k + rank + 1)
        doc_map[did] = doc

    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)[:top_k]
    return [doc_map[did] for did in sorted_ids]
