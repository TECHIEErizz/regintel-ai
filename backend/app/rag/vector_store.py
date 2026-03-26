from langchain_community.vectorstores import Chroma
from app.rag.embeddings import get_embedding_model
import uuid


def store_chunks(chunks, collection_name):
    """
    Store chunks into a specific collection
    """

    embedding_model = get_embedding_model()

    ids = [str(uuid.uuid4()) for _ in chunks]

    vectordb = Chroma.from_texts(
        texts=chunks,
        embedding=embedding_model,
        ids=ids,
        collection_name=collection_name,
        persist_directory="./chroma_db"
    )

    vectordb.persist()

    return vectordb