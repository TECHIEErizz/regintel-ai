import os
from app.rag.chunker import chunk_document
from app.rag.vector_store import store_chunks


def process_document(text: str, collection_name: str):
    """
    Process document into specific collection
    """
    if os.path.exists(f"./chroma_db/{collection_name}"):
        print("Already processed, skipping embedding")
        return

    if not text or len(text.strip()) == 0:
        raise ValueError("Empty document text")

    chunks = chunk_document(text)

    store_chunks(chunks, collection_name)

    return {
        "status": "success",
        "collection": collection_name,
        "num_chunks": len(chunks)
    }