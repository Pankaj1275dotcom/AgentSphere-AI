"""
Centralized LLM provider with automatic Gemini → Groq fallback.
When Gemini hits a rate limit / quota exhaustion, all subsequent calls
silently switch to Groq with zero error shown to the user.
"""
from langchain_core.prompts import PromptTemplate
from pydantic import SecretStr
from typing import Any, cast
from utils.config import GEMINI_MODEL, GOOGLE_API_KEY, GROQ_API_KEY, GROQ_MODEL
from utils.helpers import get_logger

logger = get_logger(__name__)

_gemini_llm = None
_groq_llm = None
_gemini_available = True

RATE_LIMIT_KEYWORDS = [
    "429", "quota", "resource_exhausted", "rate limit",
    "too many requests", "exhausted", "ratelimitexceeded",
]


def _is_rate_limit(e: Exception) -> bool:
    return any(kw in str(e).lower() for kw in RATE_LIMIT_KEYWORDS)


def _extract_raw_content(raw_content):
    if isinstance(raw_content, list):
        return " ".join(str(item) for item in raw_content)
    return str(raw_content)


def _get_gemini(temperature: float = 0.2):
    global _gemini_llm
    if _gemini_llm is None:
        from langchain_google_genai import ChatGoogleGenerativeAI
        # Create a google.genai client configured to not retry, so rate-limit
        # errors fail fast and we can fall back to Groq immediately.
        import google.genai.client as genai_client
        import google.genai.types as genai_types

        http_opts = {"retryOptions": {"attempts": 0}}
        genai_client_instance = genai_client.Client(api_key=GOOGLE_API_KEY, http_options=cast(Any, http_opts))

        _gemini_llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            client=genai_client_instance,
            temperature=temperature,
            streaming=True,
        )
    return _gemini_llm


def _get_groq(temperature: float = 0.2):
    global _groq_llm
    if _groq_llm is None:
        from langchain_groq import ChatGroq
        groq_kwargs = {
            "model": GROQ_MODEL,
            "api_key": SecretStr(GROQ_API_KEY),
            "temperature": temperature,
            "streaming": True,
        }
        _groq_llm = cast(Any, ChatGroq)(**groq_kwargs)
    return _groq_llm


def invoke_chain(prompt_template: str, inputs: dict, temperature: float = 0.2) -> str:
    """
    Build a prompt | LLM chain and invoke it.
    Silently falls back to Groq if Gemini is rate-limited.
    """
    global _gemini_available, _gemini_llm

    prompt = PromptTemplate.from_template(prompt_template)

    if _gemini_available:
        try:
            chain = prompt | _get_gemini(temperature)
            result = chain.invoke(inputs)
            return _extract_raw_content(getattr(result, "content", result)).strip()
        except Exception as e:
            if _is_rate_limit(e):
                # Silent failover to Groq: mark Gemini unavailable and clear instance.
                _gemini_available = False
                _gemini_llm = None
            else:
                raise

    # Groq fallback
    chain = prompt | _get_groq(temperature)
    result = chain.invoke(inputs)
    return _extract_raw_content(getattr(result, "content", result)).strip()


def stream_chain(prompt_template: str, inputs: dict, temperature: float = 0.2):
    """
    Stream responses token-by-token.
    Silently falls back to Groq if Gemini is rate-limited.
    """
    global _gemini_available, _gemini_llm

    prompt = PromptTemplate.from_template(prompt_template)

    if _gemini_available:
        try:
            chain = prompt | _get_gemini(temperature)
            for chunk in chain.stream(inputs):
                content = _extract_raw_content(getattr(chunk, "content", ""))
                if content:
                    yield content
            return
        except Exception as e:
            if _is_rate_limit(e):
                # Silent failover to Groq during streaming.
                _gemini_available = False
                _gemini_llm = None
            else:
                raise

    # Groq fallback
    chain = prompt | _get_groq(temperature)
    for chunk in chain.stream(inputs):
        content = _extract_raw_content(getattr(chunk, "content", ""))
        if content:
            yield content

