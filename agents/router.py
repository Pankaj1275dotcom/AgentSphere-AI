from agents.state import AgentState
from rag.ingest import get_indexed_stats
from utils.llm import invoke_chain
from utils.prompts import ROUTER_PROMPT
from utils.helpers import get_logger

logger = get_logger(__name__)


def route_question(state: AgentState) -> AgentState:
    """Decide whether to use PDF retrieval or web search."""
    question = state["question"]
    stats = get_indexed_stats()

    if stats["total_chunks"] == 0:
        logger.info("No documents indexed — routing to web.")
        return {**state, "route": "web"}

    doc_summary = ", ".join(stats["documents"]) if stats["documents"] else "general documents"

    try:
        raw = invoke_chain(ROUTER_PROMPT, {"question": question, "doc_summary": doc_summary}, temperature=0)
        raw = raw.strip().lower()
        route = "pdf" if "pdf" in raw else "web"
        logger.info(f"Router decision: '{raw}' → route='{route}'")
    except Exception as e:
        logger.error(f"Routing failed: {e}. Defaulting to web.")
        route = "web"

    return {**state, "route": route, "doc_summary": doc_summary}


def decide_route(state: AgentState) -> str:
    """LangGraph conditional edge — returns the route string."""
    return state.get("route") or "web"
