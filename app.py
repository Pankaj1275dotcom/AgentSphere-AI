import os
import streamlit as st
from agents.graph import run_agent_stream
from rag.ingest import ingest_pdf, get_indexed_stats, delete_indexed_document
from memory.chat_memory import (
    init_memory, add_message, get_history,
    new_chat, load_chat, clear_current_chat, export_chat,
    list_sessions, delete_session,
)
from utils.helpers import ensure_dirs, get_logger
logger = get_logger(__name__)
ensure_dirs("data", "chroma_db", "uploads", os.path.join("data", "chats"))
st.set_page_config(
    page_title="Agentic RAG Chatbot",
    page_icon="🤖",
    layout="wide",
)
init_memory(st.session_state)
if "processing" not in st.session_state:
    st.session_state.processing = False
# Sidebar
with st.sidebar:

    #  New Chat button
    if st.button("✏️ New Chat", use_container_width=True, type="primary"):
        new_chat(st.session_state)
        st.rerun()

    st.markdown("---")

    # Chat history
    st.subheader("💬 Chat History")
    sessions = list_sessions()

    if not sessions:
        st.caption("No saved chats yet.")
    else:
        for s in sessions:
            is_active = s["session_id"] == st.session_state.session_id
            label = ("▶ " if is_active else "") + s["title"]
            col_btn, col_del = st.columns([5, 1])
            with col_btn:
                if st.button(
                    label,
                    key=f"load_{s['session_id']}",
                    use_container_width=True,
                    type="secondary" if not is_active else "primary",
                    help=f"{s['message_count']} messages · {s['updated_at'][:10]}",
                ):
                    if not is_active:
                        load_chat(st.session_state, s["session_id"])
                        st.rerun()
            with col_del:
                if st.button(
                    "🗑",
                    key=f"del_{s['session_id']}",
                    help="Delete this chat",
                ):
                    delete_session(s["session_id"])
                    if is_active:
                        new_chat(st.session_state)
                    st.rerun()

    st.markdown("---")

    # Document Manager
    st.subheader("📚 Document Manager")

    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more PDFs to query",
    )
    if st.button("⚙️ Process PDFs", disabled=not uploaded_files, use_container_width=True):
        st.session_state.processing = True
        progress = st.progress(0, text="Starting…")
        results = []

        for i, f in enumerate(uploaded_files):
            progress.progress(i / len(uploaded_files), text=f"Processing '{f.name}'…")
            success, msg, n_chunks = ingest_pdf(f.read(), f.name)
            results.append((success, msg, n_chunks))

        progress.progress(1.0, text="Done!")

        for success, msg, n_chunks in results:
            if success:
                st.success(f"✅ {msg}")
            else:
                st.warning(f"⚠️ {msg}")

        st.session_state.processing = False
        st.rerun()

    st.markdown("---")
    st.subheader("📊 Indexed Documents")
    stats = get_indexed_stats()

    col1, col2 = st.columns(2)
    col1.metric("Documents", stats["total_documents"])
    col2.metric("Chunks", stats["total_chunks"])

    if stats["documents"]:
        st.caption("Files in index:")
        for doc in stats["documents"]:
            col_doc, col_del = st.columns([6, 1])
            with col_doc:
                st.markdown(f"- 📄 `{doc}`")
            with col_del:
                if st.button(
                    "Delete",
                    key=f"delete_doc_{doc}",
                    use_container_width=True,
                ):
                    success, msg = delete_indexed_document(doc)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                    st.rerun()
    else:
        st.info("No documents indexed yet.")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            clear_current_chat(st.session_state)
            st.rerun()
    with col_b:
        history = get_history(st.session_state)
        if history:
            st.download_button(
                label="💾 Export",
                data=export_chat(st.session_state),
                file_name=f"{st.session_state.get('chat_title', 'chat')[:30]}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.button("💾 Export", disabled=True, use_container_width=True)

    st.markdown("---")
    st.caption("Powered by Google Gemini · ChromaDB · LangGraph")

# ── Main chat area ────────────────────────────────────────────────────────────
title = st.session_state.get("chat_title", "New Chat")
st.title("🤖 Agentic RAG Chatbot")
st.caption(f"**{title}** · Ask questions about your PDFs or anything on the web.")

history = get_history(st.session_state)
if not history:
    with st.chat_message("assistant"):
        st.markdown(
            "Hello! I'm your AI research assistant. Upload PDFs in the sidebar and ask me anything. "
            "I'll automatically decide whether to answer from your documents or search the web. 🚀"
        )

for msg in history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question…", disabled=st.session_state.processing):
    add_message(st.session_state, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stats = get_indexed_stats()

        with st.status("Thinking…", expanded=False) as status:
            try:
                st.write("🔀 Routing question…")
                route, stream = run_agent_stream(prompt)
                if route == "pdf":
                    st.write(f"📄 Searching {stats['total_documents']} document(s)…")
                    status.update(label="✅ Answered from PDFs", state="complete")
                else:
                    st.write("🌐 Performing web search…")
                    status.update(label="✅ Answered from web search", state="complete")
            except Exception as e:
                logger.error(f"Agent error: {e}")
                stream = iter([f"❌ An error occurred: {e}"])
                status.update(label="Error", state="error")

        placeholder = st.empty()
        text_so_far = ""
        for chunk in stream:
            text_so_far += str(chunk)
            placeholder.markdown(text_so_far)
        if text_so_far == "":
            placeholder.markdown("Sorry, I couldn't generate an answer.")
        answer = text_so_far

    add_message(st.session_state, "assistant", answer)
