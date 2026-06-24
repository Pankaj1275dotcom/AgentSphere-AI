# 🚀 AgentSphere-AI

### Intelligent Agentic RAG Chatbot with Hybrid Retrieval, Web Search & Dual LLM Support

AgentSphere-AI is a production-ready Agentic Retrieval-Augmented Generation (RAG) chatbot that can answer questions from uploaded PDF documents and real-time web sources.

The system intelligently routes user queries between document retrieval and web search using LangGraph agents. It combines semantic search and keyword search through Hybrid Retrieval (BM25 + Vector Search + RRF Fusion) for highly accurate responses.

If the Gemini API becomes unavailable, the system automatically switches to Groq as a fallback LLM, ensuring uninterrupted responses.

---

## 🌐 Live Demo

**Live Application:**
https://agentsphere-ai-p5gc.onrender.com/

**GitHub Repository:**
https://github.com/Pankaj1275dotcom/AgentSphere-AI

---

## ✨ Features

### 📄 PDF Question Answering (RAG)

* Upload PDF documents through the sidebar.
* Process PDFs into a vector database.
* Ask questions directly from uploaded documents.
* Context-aware answers from document content.
* Source attribution included.

### 🌍 Real-Time Web Search

* Search the internet for current information.
* Answer questions about recent events.
* Automatically retrieves live information.
* Displays source links for transparency.

### 🔍 Hybrid Retrieval

Combines:

* BM25 Keyword Search
* Semantic Vector Search
* Reciprocal Rank Fusion (RRF)

This significantly improves retrieval accuracy compared to traditional RAG systems.

### 🤖 Agentic Workflow

Built using LangGraph agents that:

* Analyze user intent.
* Decide whether to use:

  * PDF Retrieval
  * Web Search
* Route requests automatically.

### 🔄 Dual LLM Support

#### Primary LLM

* Google Gemini

#### Fallback LLM

* Groq

If Gemini API fails or becomes unavailable, AgentSphere-AI automatically switches to Groq to ensure uninterrupted responses.

### 💬 Chat Management

* Create new chat sessions.
* View previous conversations.
* Delete chat history.
* Multi-session support.
* Context-aware memory.

### 📂 Document Management

* Upload PDFs.
* Process uploaded PDFs.
* Remove uploaded documents.
* Manage multiple documents.

### 🧠 Conversation Memory

* Maintains context during conversations.
* Supports multi-turn interactions.
* Stores session history.

### 🎨 Modern UI

* Built with Streamlit.
* Dark-themed interface.
* Sidebar-based navigation.
* Document Manager.
* Chat History Manager.
* Source attribution for every answer.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────┐
                    │   User Query    │
                    └────────┬────────┘
                             │
                             ▼
                 ┌─────────────────────┐
                 │ LangGraph Router    │
                 │       Agent         │
                 └────────┬────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
 ┌─────────────────┐            ┌─────────────────┐
 │   PDF Query     │            │   Web Query     │
 └────────┬────────┘            └────────┬────────┘
          │                              │
          ▼                              ▼
 ┌─────────────────┐          ┌──────────────────┐
 │ Hybrid Retriever│          │ DuckDuckGo Search│
 │ BM25 + Semantic │          └────────┬─────────┘
 │ + RRF Fusion    │                   │
 └────────┬────────┘                   ▼
          │                    ┌─────────────────┐
          ▼                    │ Search Results  │
 ┌─────────────────┐           └────────┬────────┘
 │    ChromaDB     │                    │
 └────────┬────────┘                    │
          └──────────────┬──────────────┘
                         ▼
              ┌──────────────────┐
              │  Gemini API      │
              │ (Primary LLM)    │
              └────────┬─────────┘
                       │
                Gemini Fails?
                       │
                       ▼
              ┌──────────────────┐
              │     Groq API     │
              │    (Fallback)    │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Final Response   │
              │ + Sources        │
              └──────────────────┘
```

---

## 🛠️ Tech Stack

| Category        | Technology                      |
| --------------- | ------------------------------- |
| Frontend        | Streamlit                       |
| Framework       | LangChain                       |
| Orchestration   | LangGraph                       |
| Vector Database | ChromaDB                        |
| Embeddings      | Google Generative AI Embeddings |
| Retrieval       | BM25 + Semantic Search + RRF    |
| Web Search      | DuckDuckGo Search (DDGS)        |
| LLM Primary     | Google Gemini                   |
| LLM Fallback    | Groq                            |
| PDF Processing  | PyPDF                           |
| Language        | Python 3.11+                    |

---

## 📂 Project Structure

```text
AgentSphere-AI/
│
├── .streamlit/
│   └── config.toml
│
├── agents/
│   ├── __init__.py
│   ├── graph.py
│   ├── router.py
│   └── state.py
│
├── memory/
│   ├── __init__.py
│   └── chat_memory.py
│
├── rag/
│   ├── __init__.py
│   ├── hybrid.py
│   ├── ingest.py
│   ├── retriever.py
│   └── vectorstore.py
│
├── tools/
│   ├── __init__.py
│   ├── pdf_tool.py
│   ├── reranker.py
│   └── web_tool.py
│
├── utils/
│   ├── __init__.py
│   ├── config.py
│   ├── helpers.py
│   ├── llm.py
│   └── prompts.py
│
├── .gitignore
├── Procfile
├── app.py
└── requirements.txt
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/Pankaj1275dotcom/AgentSphere-AI.git
cd AgentSphere-AI
```

### Create Virtual Environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux / Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file:

```env
GOOGLE_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

---

## 🚀 Deployment

### Render

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

---

## 📸 Screenshots

### 🏠 Main Interface

<img width="1303" height="587" alt="Main Interface" src="YOUR_MAIN_INTERFACE_SCREENSHOT_LINK">

Features shown:

* New Chat
* Chat History
* Document Manager
* PDF Upload
* PDF Processing
* Query Input
* Source Attribution

---

### 📄 PDF Question Answering

<img width="1296" height="610" alt="PDF QA" src="https://github.com/user-attachments/assets/e9899a02-75f8-452f-87a1-c5af434b0a21" />

The chatbot retrieves relevant chunks from uploaded PDF documents and generates context-aware answers using Hybrid Retrieval.

---

### 🌐 Real-Time Web Search

<img width="1303" height="587" alt="Web Search" src="https://github.com/user-attachments/assets/258864cd-3f13-4617-a7f9-eb9aef09b435" />

The system automatically detects web-related queries and fetches live information with source attribution.

---

## 🎯 Key Highlights

✅ Agentic RAG Architecture

✅ LangGraph-Based Query Routing

✅ Hybrid Retrieval (BM25 + Semantic + RRF)

✅ ChromaDB Vector Database

✅ PDF Question Answering

✅ Real-Time Web Search

✅ Automatic Query Classification

✅ Gemini + Groq Fallback Architecture

✅ Chat History Management

✅ New Chat Sessions

✅ Chat Deletion Support

✅ PDF Upload & PDF Removal

✅ Source Attribution

✅ Conversation Memory

✅ Streamlit Production UI

✅ Render Deployment Ready

---

## 👨‍💻 Author

### Pankaj Kumar Saini


