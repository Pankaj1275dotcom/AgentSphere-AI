import os
import json
import uuid
from typing import List, Dict, Optional
from datetime import datetime

CHATS_DIR = os.path.join("data", "chats")


def _ensure_chats_dir():
    os.makedirs(CHATS_DIR, exist_ok=True)


def _chat_path(session_id: str) -> str:
    return os.path.join(CHATS_DIR, f"{session_id}.json")


def _save_session(session_id: str, messages: List[Dict], title: str, created_at: str):
    _ensure_chats_dir()
    data = {
        "session_id": session_id,
        "title": title,
        "created_at": created_at,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": messages,
    }
    with open(_chat_path(session_id), "w") as f:
        json.dump(data, f, indent=2)


def _load_session(session_id: str) -> Optional[dict]:
    path = _chat_path(session_id)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def list_sessions() -> List[dict]:
    """Return all saved sessions sorted by most recent first."""
    _ensure_chats_dir()
    sessions = []
    for fname in os.listdir(CHATS_DIR):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(CHATS_DIR, fname)) as f:
                data = json.load(f)
            sessions.append({
                "session_id": data["session_id"],
                "title": data.get("title", "Untitled"),
                "updated_at": data.get("updated_at", ""),
                "message_count": len(data.get("messages", [])),
            })
        except Exception:
            continue
    return sorted(sessions, key=lambda x: x["updated_at"], reverse=True)


def delete_session(session_id: str):
    path = _chat_path(session_id)
    if os.path.exists(path):
        os.remove(path)


def init_memory(session_state) -> None:
    """Initialize or restore chat session from disk."""
    if "session_id" not in session_state:
        session_state.session_id = str(uuid.uuid4())
        session_state.messages = []
        session_state.chat_title = "New Chat"
        session_state.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif not session_state.get("messages"):
        # Try to restore from disk on refresh
        saved = _load_session(session_state.session_id)
        if saved:
            session_state.messages = saved["messages"]
            session_state.chat_title = saved.get("title", "New Chat")
            session_state.created_at = saved.get("created_at", "")


def add_message(session_state, role: str, content: str) -> None:
    msg = {
        "role": role,
        "content": content,
        "time": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%Y-%m-%d"),
    }
    session_state.messages.append(msg)

    # Auto-title from the first user message
    if role == "user" and session_state.get("chat_title") == "New Chat":
        session_state.chat_title = content[:50] + ("…" if len(content) > 50 else "")

    # Persist to disk immediately
    _save_session(
        session_state.session_id,
        session_state.messages,
        session_state.chat_title,
        session_state.created_at,
    )


def get_history(session_state) -> List[Dict]:
    return session_state.get("messages", [])


def new_chat(session_state) -> None:
    """Start a brand-new chat session."""
    session_state.session_id = str(uuid.uuid4())
    session_state.messages = []
    session_state.chat_title = "New Chat"
    session_state.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_chat(session_state, session_id: str) -> bool:
    """Load a previous chat session by ID."""
    saved = _load_session(session_id)
    if not saved:
        return False
    session_state.session_id = session_id
    session_state.messages = saved["messages"]
    session_state.chat_title = saved.get("title", "Untitled")
    session_state.created_at = saved.get("created_at", "")
    return True


def clear_current_chat(session_state) -> None:
    """Clear messages in the current session (keeps the session ID)."""
    session_state.messages = []
    session_state.chat_title = "New Chat"
    _save_session(
        session_state.session_id,
        [],
        "New Chat",
        session_state.created_at,
    )


def export_chat(session_state) -> str:
    lines = [
        f"Chat: {session_state.get('chat_title', '')}\n"
        f"Date: {session_state.get('created_at', '')}\n"
        f"{'='*50}\n"
    ]
    for msg in get_history(session_state):
        role = "You" if msg["role"] == "user" else "Assistant"
        lines.append(f"[{msg.get('date', '')} {msg.get('time', '')}] {role}:\n{msg['content']}\n")
    return "\n".join(lines)
