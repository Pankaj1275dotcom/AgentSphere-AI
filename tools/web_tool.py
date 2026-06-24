import re
from ddgs import DDGS
from agents.state import AgentState
from utils.llm import invoke_chain, stream_chain
from utils.prompts import WEB_SEARCH_PROMPT
from utils.helpers import get_logger

logger = get_logger(__name__)

def _normalize_search_result(result: dict) -> dict[str, str]:
    return {
        "title": result.get("title", "") or result.get("name", ""),
        "content": result.get("content", "")
        or result.get("body", "")
        or result.get("snippet", "")
        or result.get("description", ""),
        "url": result.get("url", "") or result.get("href", "") or result.get("link", ""),
    }


def normalize_query(question: str) -> str:
    normalized = question
    if re.search(r"\bcm\b", question, flags=re.IGNORECASE):
        normalized = re.sub(r"\bcm\b", "chief minister", question, flags=re.IGNORECASE)
    return normalized


def web_search_node(state: AgentState) -> AgentState:
    """Perform web search and generate an answer."""

    question = state["question"]

    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(question, max_results=5))
        results = [_normalize_search_result(r) for r in raw_results]
        logger.info(f"DDG search returned {len(results)} results.")
    except Exception as e:
        logger.error(f"DDG search failed: {e}")
        return {
            **state,
            "search_results": "",
            "answer": f"Web search failed: {e}. Please try again.",
        }

    if not results:
        return {
            **state,
            "search_results": "",
            "answer": "No reliable web search results were found.",
        }

    formatted = "\n\n".join(
        f"Title: {r.get('title', '')}\n"
        f"Content: {r.get('content', '')}\n"
        f"URL: {r.get('url', '')}"
        for r in results
    )

    try:
        answer = invoke_chain(
            WEB_SEARCH_PROMPT,
            {
                "search_results": formatted,
                "question": question,
            },
            temperature=0.0,  # factual answers
        )

    except Exception as e:
        logger.error(f"Web answer generation failed: {e}")

        answer = f"Error generating answer from web results: {e}"

    sources = (
        "\n\n---\n"
        "**Web Sources:**\n"
        + "\n".join(
            f"- [{r.get('title', 'Link')}]({r.get('url', '')})"
            for r in results[:3]
        )
    )

    full_answer = answer + sources

    return {
        **state,
        "search_results": formatted,
        "answer": full_answer,
    }


def web_search_stream(question: str):
    """Stream web-search-based answer chunks for a question."""
    normalized_question = normalize_query(question)
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(normalized_question, max_results=5))
        results = [_normalize_search_result(r) for r in raw_results]
        logger.info(f"DDG search returned {len(results)} results.")
    except Exception as e:
        yield f"Web search failed: {e}"
        return

    if not results:
        yield "No reliable web search results were found."
        return

    formatted = "\n\n".join(
        f"Title: {r.get('title', '')}\nContent: {r.get('content', '')}\nURL: {r.get('url', '')}"
        for r in results
    )

    try:
        for chunk in stream_chain(
            WEB_SEARCH_PROMPT, {"search_results": formatted, "question": question}, temperature=0.0
        ):
            yield chunk
    except Exception as e:
        yield f"Error generating answer from web results: {e}"
        return

    sources = (
        "\n\n---\n**Web Sources:**\n"
        + "\n".join(f"- [{r.get('title', 'Link')}]({r.get('url', '')})" for r in results[:3])
    )
    yield sources