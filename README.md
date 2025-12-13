# RAG-Mini — Simple Document Q&A (Gemini + Local Vector Store)

A from-scratch Retrieval-Augmented Generation (RAG) system for querying documents using local embeddings and Google Gemini.

No LangChain.
No Pinecone / Qdrant Cloud.
No managed vector DB.

Embeddings run fully offline, vectors are stored locally, and Gemini is used only for final answers.



🧩 Architecture Overview
React UI (Vite)
   │
   │  REST API (Axios)
   ▼
FastAPI Backend
   │
   ├─ Local embeddings (SentenceTransformers)
   ├─ NumPy vector store (./lite_index)
   ├─ Retrieval (cosine similarity)
   └─ Gemini (answer synthesis only)

## Features
- **Document formats:** `.txt`, `.md`, `.pdf`
- **Smart chunking:** 800 chars with 200 overlap (configurable)
- **Semantic search:** `sentence-transformers/all-MiniLM-L6-v2` (local, no API)
- **Local vector store:** tiny NumPy index on disk (`./lite_index`) — no services to run
- **Gemini answers:** concise responses grounded in retrieved context
- **CLI chat:** ask questions in your terminal
- **Robustness:** prompt budgets + retries + extractive fallback so you always get something

✨ What This Project Does

Upload documents (.pdf, .txt, .md)

Chunk + embed them locally using Sentence Transformers

Store vectors in a lightweight NumPy index

Retrieve the most relevant chunks per query

Generate structured, grounded answers using Gemini

Show sources used for every answer

Render clean Markdown summaries in a React UI

This is a real, production-style RAG architecture, just stripped down to essentials.

📄 Document Ingestion

Supports PDF, Markdown, and Text

OCR-normalized (fixes broken PDF spacing)

Smart chunking (800 chars, 200 overlap)

🔍 Retrieval

Local semantic search using all-MiniLM-L6-v2

No external services required

Transparent chunk retrieval

🤖 Answer Generation

Gemini 2.5 Flash

Uses only retrieved context

Structured summaries with headings and bullets

Safe fallback behavior

🖥️ UI

React + Vite

Markdown-rendered answers

Collapsible Sources panel

Clean chat experience

---

## Quick Start

### 1) Clone & setup
```bash
git clone https://github.com/Sakethv7/RAG_mini
cd RAG-mini
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
