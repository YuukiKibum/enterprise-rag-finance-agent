from . import get_vector_store_collection
from . import create_embeddings

def retrieve_context(query: str, k: int = 5):
    collection = get_vector_store_collection.get_vector_store_collection()
    [query_embedding] = create_embeddings.embed_texts([query])

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    return results["documents"][0], results["metadatas"][0]