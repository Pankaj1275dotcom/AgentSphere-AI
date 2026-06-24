from typing import List, Optional
from typing_extensions import TypedDict
from langchain_core.documents import Document


class AgentState(TypedDict):
    question: str
    route: Optional[str]
    documents: List[Document]
    search_results: Optional[str]
    answer: Optional[str]
    doc_summary: Optional[str]
