from pathlib import Path
from chromadb import PersistentClient


def get_project_root() -> Path:
    """
    Finds the project root folder.

    Current file is expected to be inside:
    src/chroma_db_functionalities/get_vector_store_collection.py

    So parents[2] should point to the main project folder:
    serco/
    """
    return Path(__file__).resolve().parents[2]


def get_chroma_db_path() -> str:
    """
    Returns a stable absolute path for ChromaDB.
    This prevents creating different chroma_db folders depending on terminal location.
    """
    project_root = get_project_root()
    chroma_path = project_root / "chroma_db"

    chroma_path.mkdir(parents=True, exist_ok=True)

    return str(chroma_path)


def get_vector_store_collection():
    """
    Connects to ChromaDB using a fixed project-root path.
    """
    client = PersistentClient(path=get_chroma_db_path())

    return client.get_or_create_collection(
        name="rag_docs",
        metadata={"hnsw:space": "cosine"}
    )