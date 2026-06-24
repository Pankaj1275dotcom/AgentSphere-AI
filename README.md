# 🚀 AgentSphere-AI

### Intelligent Agentic RAG Chatbot with Hybrid Retrieval, Web Search & Dual LLM Support

AgentSphere-AI is a production-ready Agentic Retrieval-Augmented Generation (RAG) chatbot that can answer questions from uploaded PDF documents and real-time web sources.

The system intelligently routes user queries between document retrieval and web search using LangGraph agents. It combines semantic search and keyword search through Hybrid Retrieval (BM25 + Vector Search + RRF Fusion) for more accurate answers.

If the Gemini API becomes unavailable, the system automatically switches to Groq as a fallback LLM, ensuring uninterrupted responses.

---

## 🌐 Live Demo

**Live Application:** https://agentsphere-ai-p5gc.onrender.com/

**GitHub Repository:** https://github.com/Pankaj1275dotcom/AgentSphere-AI

---

## ✨ Features

### 📄 PDF Question Answering (RAG)

* Upload PDF documents
* Ask questions about uploaded content
* Context-aware answers from documents
* Source attribution included

### 🌍 Real-Time Web Search

* Searches the web for current information
* Provides source links
* Handles recent events and live information

### 🔍 Hybrid Retrieval

Combines:

* BM25 Keyword Search
* Semantic Vector Search
* Reciprocal Rank Fusion (RRF)

This improves retrieval accuracy compared to traditional RAG systems.

### 🤖 Agentic Workflow

Built using LangGraph agents that:

* Analyze user intent
* Decide whether to use RAG or Web Search
* Route requests intelligently

### 🔄 Dual LLM Support

Primary Model:

* Google Gemini

Fallback Model:

* Groq

If Gemini fails, the chatbot automatically switches to Groq without interrupting the user experience.

### 🧠 Chat Memory

* Maintains conversation context
* Stores chat history
* Supports multi-turn conversations

### 🎨 Modern UI

* Built with Streamlit
* Dark theme interface
* Chat history management
* PDF document manager

---

## 🏗️ System Architecture

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
| Orchestration   | LangGraph                       |
| Framework       | LangChain                       |
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

Linux/Mac:

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

### PDF Question Answering

(Add Screenshot Here)

### Web Search Answers

(Add Screenshot Here)

### Hybrid Retrieval Workflow

(Add Screenshot Here)

---

## 🎯 Key Highlights

* Agentic RAG Architecture
* Hybrid Retrieval System
* Real-Time Web Search
* Gemini + Groq Fallback
* Chat Memory Support
* Source Attribution
* Streamlit UI
* ChromaDB Vector Storage
* LangGraph Workflow

---

## 👨‍💻 Author

**Pankaj Kumar Saini**

