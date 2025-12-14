from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from rag_simple import SimpleRAG, _read_pdf
import shutil
import os

# ------------------- Lifespan ---------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔁 Server starting...")
    try:
        print("📚 Ingesting existing documents...")
        rag.ingest_folder("documents")
        print("✅ Startup ingestion complete")
    except Exception as e:
        print(f"⚠️ Startup ingestion failed: {e}")
    yield
    print("🛑 Server shutting down")

# ------------------- App ---------------------

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = SimpleRAG()
os.makedirs("documents", exist_ok=True)

# ------------------- Schemas ---------------------

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    chunks: list

class UploadResponse(BaseModel):
    message: str
    filename: str

# ------------------- Routes ---------------------

@app.get("/")
def health():
    return {"status": "ok", "message": "RAG server running"}

@app.get("/documents/status")
def documents_status():
    has_docs = rag.store.vectors is not None and len(rag.store.payloads) > 0
    return {
        "has_documents": has_docs,
        "document_count": len(set(p["source"] for p in rag.store.payloads)) if has_docs else 0
    }

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    try:
        path = os.path.join("documents", file.filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        if file.filename.lower().endswith(".pdf"):
            text = _read_pdf(path)
        else:
            text = open(path, "r", encoding="utf-8", errors="ignore").read()

        rag.ingest_text(text, file.filename)

        return UploadResponse(
            message="Document uploaded and indexed",
            filename=file.filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    answer, chunks = rag.ask(req.question, return_chunks=True)
    return AskResponse(answer=answer, chunks=chunks)

@app.post("/reset")
def reset():
    rag.recreate_collection()
    return {"message": "Index reset"}
