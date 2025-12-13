from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_simple import SimpleRAG, _read_pdf, normalize_ocr_text
import shutil
import os

app = FastAPI()

# ------------------- CORS ---------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- Init ---------------------
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

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    try:
        path = os.path.join("documents", file.filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        ext = os.path.splitext(file.filename)[1].lower()
        if ext == ".pdf":
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


@app.get("/")
def health():
    return {"status": "ok", "message": "RAG server running"}
