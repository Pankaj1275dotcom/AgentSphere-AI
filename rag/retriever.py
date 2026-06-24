from typing import List

from langchain_core.documents import Document

from rag.vectorstore import get_vectorstore
from rag.hybrid import bm25_search, reciprocal_rank_fusion
from utils.config import TOP_K_RETRIEVAL, TOP_K_FINAL
from utils.helpers import get_logger

logger = get_logger(__name__)


def hybrid_retrieve(query: str) -> List[Document]:
    """Perform hybrid retrieval: semantic + BM25 + RRF."""
    try:
        vs = get_vectorstore()
        semantic_docs = vs.similarity_search(query, k=TOP_K_RETRIEVAL)
        logger.info(f"Semantic search returned {len(semantic_docs)} docs.")
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        semantic_docs = []

    try:
        bm25_docs = bm25_search(query, top_k=TOP_K_RETRIEVAL)
        logger.info(f"BM25 search returned {len(bm25_docs)} docs.")
    except Exception as e:
        logger.error(f"BM25 search failed: {e}")
        bm25_docs = []

    if not semantic_docs and not bm25_docs:
        return []

    fused = reciprocal_rank_fusion(semantic_docs, bm25_docs, top_k=TOP_K_FINAL)
    logger.info(f"RRF fusion returned {len(fused)} docs.")
    return fused
