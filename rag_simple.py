# rag_simple.py  (Gemini version - Fixed)
import os
import re
import glob
import uuid
import hashlib
from typing import List, Dict

import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from pypdf import PdfReader

# Google AI Studio (Gemini)
import google.generativeai as genai


# ---------------------------
# helpers
# ---------------------------

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
    """
    Simple sliding-window chunker:
      - chunk_size: characters per chunk
      - overlap:    chars to carry over into the next chunk
    """
    text = text.strip()
    if not text:
        return []
    out, i, n = [], 0, len(text)
    while i < n:
        j = min(i + chunk_size, n)
        out.append(text[i:j])
        if j == n:
            break
        i = max(0, j - overlap)
    return out


def _point_id(source: str, chunk_id: int) -> int:
    """Deterministic 64-bit ID for (source, chunk_id) so re-ingest upserts instead of duplicating."""
    h = hashlib.blake2b(f"{source}:{chunk_id}".encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(h, "big", signed=False)


# ---- File readers ----

def _read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def _read_md(path: str) -> str:
    text = _read_txt(path)
    # light cleanup: strip code fences, convert [text](url) -> text, drop leading '#'
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    return text

def _read_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for p in reader.pages:
        pages.append(p.extract_text() or "")
    return "\n".join(pages)


# ---------------------------
# RAG
# ---------------------------

class SimpleRAG:
    def __init__(
        self,
        collection_name: str = "mini_docs",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        use_embedded_qdrant: bool = True,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        qdrant_location: str = "./qdrant_data",
    ):
        """
        Minimal, framework-free RAG:
          - Sentence-Transformers (local, free) for embeddings
          - Qdrant (embedded) for vector search
          - Google AI Studio (Gemini) for final answer generation
        """
        load_dotenv()

        # 1) Embeddings (local)
        self.embedder = SentenceTransformer(embedding_model)
        self.dim = self.embedder.get_sentence_embedding_dimension()

        # 2) Vector DB (Qdrant) - Fixed initialization
        if use_embedded_qdrant:
            # Handle in-memory case
            if qdrant_location != ":memory:":
                # Ensure we use a relative path to avoid Windows path parsing issues
                if os.path.isabs(qdrant_location):
                    qdrant_location = os.path.relpath(qdrant_location)
                os.makedirs(qdrant_location, exist_ok=True)
            # Force embedded mode with explicit parameters
            self.qdrant = QdrantClient(
                location=qdrant_location,
                prefer_grpc=False,  # Use REST API instead of gRPC
                timeout=30,         # Increase timeout
                force_disable_check_same_thread=True  # For SQLite threading
            )
        else:
            # Only use remote if explicitly requested
            self.qdrant = QdrantClient(
                host=qdrant_host, 
                port=qdrant_port,
                prefer_grpc=False,
                timeout=30
            )

        self.collection = collection_name
        self._ensure_collection()

        # 3) LLM (Gemini) for the final answer
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY missing in environment/.env")
        genai.configure(api_key=api_key)

        gemini_model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.model = genai.GenerativeModel(
            model_name=gemini_model_name,
            system_instruction=(
                "Answer in exactly 1-2 sentences. Be direct and concise. "
                "Use only the provided context. Cite sources as [filename] only once per source. "
                "No repetition. No excessive detail. No chunk numbers."
            ),
        )
        # Optional: tune outputs for maximum brevity
        self.generation_config = {
            "temperature": 0.0,      # Most deterministic
            "top_p": 0.7,           
            "max_output_tokens": 80,  # Very short responses
        }

    # ----- Qdrant setup -----
    def _ensure_collection(self):
        try:
            existing = [c.name for c in self.qdrant.get_collections().collections]
            if self.collection not in existing:
                self.qdrant.create_collection(
                    collection_name=self.collection,
                    vectors_config=qm.VectorParams(size=self.dim, distance=qm.Distance.COSINE),
                )
        except Exception as e:
            print(f"Error ensuring collection: {e}")
            raise

    # ----- Maintenance -----
    def recreate_collection(self):
        """Wipes and recreates the collection (use when starting fresh)."""
        try:
            self.qdrant.delete_collection(self.collection)
        except Exception:
            pass
        self._ensure_collection()

    # ---- Embedding helpers ----
    def embed(self, texts: List[str]) -> np.ndarray:
        return self.embedder.encode(texts, normalize_embeddings=True, convert_to_numpy=True)

    # ---- Ingestion ----
    def _load_file_text(self, path: str) -> str:
        ext = os.path.splitext(path.lower())[1]
        if ext == ".txt":
            return _read_txt(path)
        if ext == ".md":
            return _read_md(path)
        if ext == ".pdf":
            return _read_pdf(path)
        # fallback
        return _read_txt(path)

    def ingest_folder(self, folder: str = "documents") -> Dict:
        """Read .txt/.md/.pdf, chunk, embed, and upsert to Qdrant."""
        patterns = ["*.txt", "*.md", "*.pdf"]
        paths = []
        for pat in patterns:
            paths.extend(glob.glob(os.path.join(folder, pat)))
        paths = sorted(paths)

        total_chunks, details = 0, []
        for p in paths:
            try:
                text = self._load_file_text(p)
            except Exception as e:
                print(f"[skip] Failed reading {p}: {e}")
                continue

            chunks = chunk_text(text, chunk_size=800, overlap=200)
            if not chunks:
                continue

            vecs = self.embed(chunks)
            src_name = os.path.basename(p)
            doc_id = str(uuid.uuid4())

            points = []
            for i, (ch, v) in enumerate(zip(chunks, vecs)):
                points.append(
                    qm.PointStruct(
                        id=_point_id(src_name, i),
                        vector=v.tolist(),
                        payload={
                            "doc_id": doc_id,
                            "chunk_id": i,
                            "text": ch,
                            "source": src_name,
                        },
                    )
                )

            if points:
                self.qdrant.upsert(collection_name=self.collection, points=points)
                total_chunks += len(points)
                details.append({"file": src_name, "chunks": len(points)})

        return {"files_indexed": len(paths), "chunks_indexed": total_chunks, "details": details}

    # ---- Retrieval ----
    def retrieve(self, question: str, k: int = 5) -> List[Dict]:
        qv = self.embed([question])[0].tolist()
        hits = self.qdrant.search(
            collection_name=self.collection,
            query_vector=qv,
            limit=k,
            with_payload=True,
        )
        out = []
        for h in hits:
            pl = h.payload or {}
            out.append(
                {
                    "score": h.score,
                    "source": pl.get("source", ""),
                    "chunk_id": pl.get("chunk_id", -1),
                    "text": pl.get("text", ""),
                }
            )
        return out

    # ---- Answering (Gemini) ----
    def answer(self, question: str, k: int = 2) -> Dict:  # Reduced from k=5 to k=2
        contexts = self.retrieve(question, k=k)
        context_block = "\n\n---\n\n".join(
            f"Source: {c['source']}\n{c['text']}" for c in contexts
        )
        user_content = f"Question: {question}\n\nContext:\n{context_block}\n\nProvide a brief, clear answer with source citations."

        try:
            resp = self.model.generate_content(
                user_content,
                generation_config=self.generation_config,
            )
            text = getattr(resp, "text", None)
            if not text and getattr(resp, "candidates", None):
                # Fallback extraction
                cand = resp.candidates[0]
                parts = getattr(cand.content, "parts", []) or []
                text = "".join(getattr(p, "text", "") for p in parts) or "No text returned."
        except Exception as e:
            text = f"Generation error: {e}"

        return {"question": question, "matches": contexts, "response": text}