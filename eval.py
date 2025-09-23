# eval.py
import time
from rag_simple import SimpleRAG

def preview(text, n=140):
    t = " ".join(text.split())
    return (t[:n] + "…") if len(t) > n else t

if __name__ == "__main__":
    rag = SimpleRAG(use_embedded_qdrant=True)

    print("Enter a query (blank to quit).")
    while True:
        q = input("Q: ").strip()
        if not q:
            break

        t0 = time.perf_counter()
        hits = rag.retrieve(q, k=8)     # just retrieval (no LLM)
        t1 = time.perf_counter()

        print(f"\nTop matches (k=8) — retrieval time: {(t1 - t0)*1000:.1f} ms")
        for i, h in enumerate(hits, 1):
            print(f"{i:>2}. score={h['score']:.4f}  {h['source']}  chunk={h['chunk_id']}")
            print(f"    {preview(h['text'])}")
        print()
