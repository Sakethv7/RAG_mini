from rag_simple import SimpleRAG
import google.generativeai as genai

if __name__ == "__main__":
    rag = SimpleRAG(use_embedded_qdrant=True, qdrant_location=":memory:")
    rag.ingest_folder("documents")
    
    # Override for cleaner responses
    rag.model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        system_instruction="Answer briefly and clearly in 1-2 sentences using the provided context."
    )
    
    while True:
        q = input("Q: ").strip()
        if not q: break
        out = rag.answer(q, k=2)
        print(f"A: {out['response']}\n")