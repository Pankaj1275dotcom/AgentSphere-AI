import hashlib
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

def compute_file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

def ensure_dirs(*dirs: str) -> None:
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def format_sources(documents) -> str:
    if not documents:
        return ""
    seen = set()
    lines = ["\n\n---\n**Sources:**"]
    for doc in documents:
        meta = doc.metadata if hasattr(doc, "metadata") else {}
        source = meta.get("source", "Unknown")
        page = meta.get("page", None)
        key = (source, page)
        if key not in seen:
            seen.add(key)
            page_str = f", page {page + 1}" if page is not None else ""
            lines.append(f"- 📄 `{source}`{page_str}")
    return "\n".join(lines)
