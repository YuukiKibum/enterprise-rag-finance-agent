from chromadb import PersistentClient # ChromaDB client for storing embeddings

def get_vector_store_collection():
    """
    Connects to ChromaDB (persistent on disk) and returns a collection.
    A collection is like a "table" where we store all our document chunks.
    """
    client = PersistentClient(path="./chroma_db")  # Creates/opens a folder for the DB

    return client.get_or_create_collection(
        name="rag_docs",                         # Name of your vector collection
        metadata={"hnsw:space": "cosine"}        # Use cosine similarity (best for embeddings)
    )

