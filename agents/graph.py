from langgraph.graph import StateGraph, END

from agents.state import AgentState
from agents.router import route_question, decide_route
from tools.pdf_tool import pdf_retrieval_node, pdf_retrieval_stream
from tools.web_tool import web_search_node, web_search_stream
from utils.helpers import get_logger

logger = get_logger(__name__)

_graph = None


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("router", route_question)
    workflow.add_node("pdf_retrieval", pdf_retrieval_node)
    workflow.add_node("web_search", web_search_node)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        decide_route,
        {
            "pdf": "pdf_retrieval",
            "web": "web_search",
        },
    )

    workflow.add_edge("pdf_retrieval", END)
    workflow.add_edge("web_search", END)

    return workflow.compile()


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
        logger.info("LangGraph compiled successfully.")
    return _graph


def run_agent_stream(question: str):
    """Stream a response from the agentic RAG pipeline."""
    stats = {"documents": [], "total_documents": 0, "total_chunks": 0}
    try:
        # Reuse the router logic to pick the route.
        state: AgentState = {
            "question": question,
            "route": None,
            "documents": [],
            "search_results": None,
            "answer": None,
            "doc_summary": None,
        }
        routed = route_question(state)
        route = routed.get("route", "web")
    except Exception:
        route = "web"

    if route == "pdf":
        return route, pdf_retrieval_stream(question)
    return route, web_search_stream(question)
