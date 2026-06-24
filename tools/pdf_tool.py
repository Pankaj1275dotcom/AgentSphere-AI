from agents.state import AgentState
from rag.retriever import hybrid_retrieve
from utils.llm import invoke_chain
from utils.prompts import RAG_PROMPT
from utils.helpers import format_sources, get_logger

logger = get_logger(__name__)


def pdf_retrieval_node(state: AgentState) -> AgentState:
    """Retrieve from PDFs and generate an answer."""
    question = state["question"]
    documents = hybrid_retrieve(question)

    if not documents:
        logger.warning("No documents retrieved from hybrid search.")
        return {
            **state,
            "documents": [],
            "answer": "I couldn't find relevant information in the uploaded documents. Try rephrasing or uploading more relevant PDFs.",
        }

    context = "\n\n".join(doc.page_content for doc in documents)
    try:
        answer = invoke_chain(RAG_PROMPT, {"context": context, "question": question}, temperature=0.2)
    except Exception as e:
        logger.error(f"PDF answer generation failed: {e}")
        answer = f"Error generating answer: {e}"

    sources_text = format_sources(documents)
    full_answer = answer + sources_text

    return {**state, "documents": documents, "answer": full_answer}


def pdf_retrieval_stream(question: str):
    """Stream PDF-based answer chunks for a question."""
    documents = hybrid_retrieve(question)

    if not documents:
        yield "I couldn't find relevant information in the uploaded documents."
        return

    context = "\n\n".join(doc.page_content for doc in documents)
    try:
        for chunk in __import__("utils.llm", fromlist=["stream_chain"]).stream_chain(
            RAG_PROMPT, {"context": context, "question": question}, temperature=0.2
        ):
            yield chunk
    except Exception as e:
        yield f"Error generating answer: {e}"
        return

    sources_text = format_sources(documents)
    if sources_text:
        yield sources_text
