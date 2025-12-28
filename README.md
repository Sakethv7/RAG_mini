# RAG-Mini — Simple Document Q&A (Gemini + Local Vector Store)

A from-scratch Retrieval-Augmented Generation (RAG) system for querying documents using Google Gemini for both embeddings and answer generation, with a tiny NumPy vector store persisted on disk.

No LangChain.
No Pinecone / Qdrant Cloud.
No managed vector DB.

Embeddings are API-based (Gemini) and vectors are stored locally; set `GOOGLE_API_KEY` before running.



🧩 Architecture Overview
React UI (Vite)
   │
   │  REST API (Axios)
   ▼
FastAPI Backend
   │
   ├─ Gemini embeddings (API)
   ├─ NumPy vector store (./lite_index)
   ├─ Retrieval (cosine similarity)
   └─ Gemini (answer synthesis)

## Features
- **Document formats:** `.txt`, `.md`, `.pdf`
- **Smart chunking:** 800 chars with 200 overlap (configurable)
- **Semantic search:** Gemini embeddings (default) or local `sentence-transformers` + cosine similarity
- **Local vector store:** tiny NumPy index on disk (`./lite_index`) — no services to run
- **Gemini answers:** concise responses grounded in retrieved context
- **CLI chat:** ask questions in your terminal

✨ What This Project Does

Upload documents (.pdf, .txt, .md)

Chunk + embed them with Gemini embeddings

Store vectors in a lightweight NumPy index

Retrieve the most relevant chunks per query via cosine similarity

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
export GOOGLE_API_KEY=your_key_here
```

### Embedding options
- Default: Gemini embeddings (`EMBED_PROVIDER=gemini`, `GEMINI_EMBED_MODEL=models/embedding-001`), requires `GOOGLE_API_KEY`.
- Local (no embedding API calls): set `EMBED_PROVIDER=local` and optionally `LOCAL_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2`. Install the extra deps: `pip install sentence-transformers`.
