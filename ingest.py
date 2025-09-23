from rag_simple import SimpleRAG

if __name__ == "__main__":
    rag = SimpleRAG(
        use_embedded_qdrant=True,
        qdrant_location=":memory:"
    )
    result = rag.ingest_folder("documents")
    print("Ingestion completed!")
    print(result)