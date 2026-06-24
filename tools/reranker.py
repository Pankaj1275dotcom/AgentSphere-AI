"""
Cross-encoder reranker (free, local) — optional quality boost.
Used as a post-retrieval step when more precision is needed.
Falls back gracefully if sentence-transformers is unavailable.
"""
from typing import List
from langchain_core.documents import Document
from utils.helpers import get_logger

logger = get_logger(__name__)

_reranker = None


def get_reranker():
    global _reranker
    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder
            _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.info("Cross-encoder reranker loaded.")
        except Exception as e:
            logger.warning(f"Reranker not available: {e}")
            _reranker = False
    return _reranker if _reranker is not False else None


def rerank(query: str, documents: List[Document], top_k: int = 4) -> List[Document]:
    """Rerank documents using cross-encoder. Falls back to original order."""
    reranker = get_reranker()
    if reranker is None or not documents:
        return documents[:top_k]

    try:
        pairs = [(query, doc.page_content) for doc in documents]
        scores = reranker.predict(pairs)
        ranked = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in ranked[:top_k]]
    except Exception as e:
        logger.error(f"Reranking failed: {e}")
        return documents[:top_k]
