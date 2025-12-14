from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_simple import SimpleRAG, _read_pdf
import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://rag-mini-ui.onrender.com",  # ⬅️ your UI
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

@app.get("/")
def health():
    return {"status": "ok", "message": "RAG server running"}
