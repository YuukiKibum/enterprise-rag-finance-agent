from . import get_vector_store_collection
from . import load_files
from . import smart_chunking
from . import create_embeddings

import os
import hashlib
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SUPPORTED_EXTENSIONS = (".docx", ".pdf", ".xlsx", ".xls")


def generate_doc_id(path: str) -> str:
    """
    Creates a stable document ID based on the file name.
    This avoids using temporary upload folder paths as doc_id.
    """
    file_name = os.path.basename(path)
    return file_name.lower().strip()


def calculate_file_hash(path: str) -> str:
    """
    Creates a hash of the file content.
    Useful for tracking whether the same file content was uploaded again.
    """
    sha256 = hashlib.sha256()

    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


def ingest_document(path: str, doc_id: str | None = None) -> dict:
    """
    Ingests ONE document into ChromaDB.

    Steps:
    1. Load text
    2. Chunk text
    3. Create embeddings
    4. Delete old chunks for same doc_id
    5. Store fresh chunks in ChromaDB
    """

    path_obj = Path(path)
    ext = path_obj.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        return {
            "status": "skipped",
            "file_name": path_obj.name,
            "reason": f"Unsupported file type: {ext}"
        }

    collection = get_vector_store_collection.get_vector_store_collection()

    doc_id = doc_id or generate_doc_id(path)
    file_name = path_obj.name
    file_hash = calculate_file_hash(path)

    # 1) Load raw text
    full_text = load_files.load_file(path)

    if not full_text or not full_text.strip():
        return {
            "status": "skipped",
            "file_name": file_name,
            "reason": "No readable text found"
        }

    # 2) Chunk text
    chunks = smart_chunking.chunk_text_smart(full_text)

    if not chunks:
        return {
            "status": "skipped",
            "file_name": file_name,
            "reason": "No chunks created"
        }

    # 3) Create embeddings
    embeddings = create_embeddings.embed_texts(chunks)

    # 4) Delete existing chunks for this same document
    # This prevents duplicate chunks when the same file is uploaded again.
    try:
        collection.delete(where={"doc_id": doc_id})
    except Exception:
        pass

    # 5) Create stable chunk IDs
    ids = [
        f"{doc_id}__chunk_{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "doc_id": doc_id,
            "file_name": file_name,
            "file_extension": ext,
            "file_hash": file_hash,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "source_path": str(path_obj),
        }
        for i in range(len(chunks))
    ]

    # 6) Store in ChromaDB
    collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    return {
        "status": "success",
        "file_name": file_name,
        "doc_id": doc_id,
        "chunks": len(chunks),
        "file_hash": file_hash,
    }


def ingest_folder(folder_path: str) -> dict:
    """
    Recursively scans a folder and ingests all supported files.
    This works for folders with subfolders.
    """

    folder = Path(folder_path)

    results = {
        "total_found": 0,
        "successful": [],
        "skipped": [],
        "failed": [],
    }

    for path in folder.rglob("*"):
        if path.is_dir():
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            results["skipped"].append({
                "file_name": path.name,
                "reason": f"Unsupported file type: {path.suffix}"
            })
            continue

        results["total_found"] += 1

        try:
            result = ingest_document(str(path))

            if result["status"] == "success":
                results["successful"].append(result)
            else:
                results["skipped"].append(result)

        except Exception as e:
            results["failed"].append({
                "file_name": path.name,
                "reason": str(e)
            })

    return results


if __name__ == "__main__":
    result = ingest_folder("serco_files")
    print(result)