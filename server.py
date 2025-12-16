from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_simple import SimpleRAG, read_pdf   # ✅ FIXED IMPORT
import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://rag-mini-ui.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = SimpleRAG()
os.makedirs("documents", exist_ok=True)

class AskRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(req: AskRequest):
    answer = rag.ask(req.question)
    return {"answer": answer}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        path = os.path.join("documents", file.filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        if file.filename.lower().endswith(".pdf"):
            text = read_pdf(path)
        else:
            text = open(path, "r", encoding="utf-8", errors="ignore").read()

        rag.ingest_text(text, file.filename)
        return {"message": "Uploaded and indexed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health():
    return {"status": "ok", "message": "RAG server running"}
