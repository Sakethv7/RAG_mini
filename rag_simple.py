# rag_simple.py — Local NumPy RAG + Gemini (clean summaries)

import os
import re
import glob
import uuid
import json
import hashlib
from typing import List, Dict, Optional

import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import google.generativeai as genai


# ---------------------------
# Helpers
# ---------------------------

def normalize_ocr_text(text: str) -> str:
    """
    Fix broken OCR text like:
    'El ectr onic R ec or d' → 'Electronic Record'
    """
    text = re.sub(r"(?<=\w)\s(?=\w)", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
    text = text.strip()
    out, i, n = [], 0, len(text)
    while i < n:
        j = min(i + chunk_size, n)
        out.append(text[i:j])
        if j == n:
            break
        i = max(0, j - overlap)
    return out


def _read_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = [p.extract_text() or "" for p in reader.pages]
    return "\n".join(pages)


def _point_id(source: str, chunk_id: int) -> int:
    b = hashlib.blake2b(f"{source}:{chunk_id}".encode(), digest_size=8).digest()
    return int.from_bytes(b, "big", signed=True)


# ---------------------------
# Lite Vector Store
# ---------------------------

class LiteVectorStore:
    def __init__(self, index_dir="./lite_index"):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        self.vectors = None
        self.ids = None
        self.payloads = []
        self._load()

    def _load(self):
        try:
            self.vectors = np.load(f"{self.index_dir}/vectors.npy")
            self.ids = np.load(f"{self.index_dir}/ids.npy")
            with open(f"{self.index_dir}/payloads.json") as f:
                self.payloads = json.load(f)
        except:
            self.vectors, self.ids, self.payloads = None, None, []

    def _save(self):
        if self.vectors is None:
            return
        np.save(f"{self.index_dir}/vectors.npy", self.vectors)
        np.save(f"{self.index_dir}/ids.npy", self.ids)
        with open(f"{self.index_dir}/payloads.json", "w") as f:
            json.dump(self.payloads, f)

    def upsert(self, ids, vectors, payloads):
        if self.vectors is None:
            self.vectors = vectors
            self.ids = ids
            self.payloads = payloads
        else:
            self.vectors = np.vstack([self.vectors, vectors])
            self.ids = np.concatenate([self.ids, ids])
            self.payloads.extend(payloads)
        self._save()

    def search(self, qvec, k=5):
        sims = np.dot(self.vectors, qvec)
        idxs = np.argsort(-sims)[:k]
        return [{**self.payloads[i], "score": float(sims[i])} for i in idxs]

    def reset(self):
        self.vectors, self.ids, self.payloads = None, None, []
        self._save()


# ---------------------------
# SimpleRAG
# ---------------------------

class SimpleRAG:
    def __init__(self, index_dir="./lite_index"):
        load_dotenv()

        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.store = LiteVectorStore(index_dir)

        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",
            system_instruction=(
                "You are a document analysis assistant.\n"
                "Use ONLY the provided context. Do not use outside knowledge.\n\n"
                "When asked for a summary:\n"
                "- Start with a short overview paragraph (2–3 sentences)\n"
                "- Then provide a structured summary using markdown headings (##)\n"
                "- Use bullet points where appropriate\n\n"
                "If information is missing or unclear, say:\n"
                "'Not found in the provided document.'"
            )
        )

    def embed(self, texts):
        return self.embedder.encode(texts, normalize_embeddings=True).astype(np.float32)

    def ingest_text(self, text: str, source: str):
        text = normalize_ocr_text(text)
        chunks = chunk_text(text)
        vecs = self.embed(chunks)

        ids = np.array([_point_id(source, i) for i in range(len(chunks))])
        payloads = [
            {"source": source, "chunk_id": i, "text": ch}
            for i, ch in enumerate(chunks)
        ]

        self.store.upsert(ids, vecs, payloads)

    def retrieve(self, question, k=5):
        qv = self.embed([question])[0]
        return self.store.search(qv, k)

    def ask(self, question, return_chunks=False):
        contexts = self.retrieve(question)

        context_text = "\n\n".join(
            f"[{c['source']}]\n{c['text']}" for c in contexts
        )

        prompt = f"""
Use the context below to answer clearly and concisely.

Question:
{question}

Context:
{context_text}
"""

        resp = self.model.generate_content(prompt)
        answer = resp.text.strip()

        if return_chunks:
            return answer, contexts
        return answer

    def recreate_collection(self):
        self.store.reset()
