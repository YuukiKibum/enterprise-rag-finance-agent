from . import get_vector_store_collection


def get_all_metadatas(batch_size: int = 1000) -> list[dict]:
    """
    Reads all metadata records from ChromaDB in batches.
    Each chunk stored in ChromaDB has one metadata record.
    """
    collection = get_vector_store_collection.get_vector_store_collection()

    total_chunks = collection.count()
    all_metadatas = []

    for offset in range(0, total_chunks, batch_size):
        result = collection.get(
            include=["metadatas"],
            limit=batch_size,
            offset=offset
        )

        metadatas = result.get("metadatas", [])

        if metadatas:
            all_metadatas.extend(metadatas)

    return all_metadatas


def get_all_ids(batch_size: int = 1000) -> list[str]:
    """
    Reads all ChromaDB chunk IDs in batches.
    Used when deleting all vector DB contents.
    """
    collection = get_vector_store_collection.get_vector_store_collection()

    total_chunks = collection.count()
    all_ids = []

    for offset in range(0, total_chunks, batch_size):
        result = collection.get(
            limit=batch_size,
            offset=offset
        )

        ids = result.get("ids", [])

        if ids:
            all_ids.extend(ids)

    return all_ids


def get_vector_db_summary() -> dict:
    """
    Returns summary information about documents stored in ChromaDB.
    """
    collection = get_vector_store_collection.get_vector_store_collection()

    total_chunks = collection.count()
    metadatas = get_all_metadatas()

    files = {}

    for metadata in metadatas:
        if not metadata:
            continue

        doc_id = metadata.get("doc_id", "unknown_doc_id")
        file_name = metadata.get("file_name", "unknown_file")
        file_extension = metadata.get("file_extension", "")
        file_hash = metadata.get("file_hash", "")

        if doc_id not in files:
            files[doc_id] = {
                "doc_id": doc_id,
                "file_name": file_name,
                "file_extension": file_extension,
                "file_hash": file_hash,
                "chunk_count": 0,
            }

        files[doc_id]["chunk_count"] += 1

    file_list = list(files.values())

    file_list = sorted(
        file_list,
        key=lambda x: x["file_name"].lower()
    )

    return {
        "total_files": len(file_list),
        "total_chunks": total_chunks,
        "files": file_list,
    }


def format_vector_db_summary() -> str:
    """
    Converts the ChromaDB summary into readable text.
    """
    summary = get_vector_db_summary()

    if summary["total_files"] == 0:
        return "No files are currently stored in the ChromaDB knowledge base."

    output = []
    output.append("ChromaDB Knowledge Base Summary")
    output.append("")
    output.append(f"Total files: {summary['total_files']}")
    output.append(f"Total chunks: {summary['total_chunks']}")
    output.append("")
    output.append("Files stored:")

    for i, file in enumerate(summary["files"], start=1):
        output.append(
            f"{i}. {file['file_name']} "
            f"- {file['chunk_count']} chunks"
        )

    return "\n".join(output)


def delete_document_from_vector_db(doc_id: str) -> dict:
    """
    Deletes one document from ChromaDB using doc_id.
    This deletes all chunks belonging to that file.
    """
    collection = get_vector_store_collection.get_vector_store_collection()

    before_count = collection.count()

    collection.delete(
        where={"doc_id": doc_id}
    )

    after_count = collection.count()
    deleted_chunks = before_count - after_count

    return {
        "status": "success",
        "doc_id": doc_id,
        "deleted_chunks": deleted_chunks,
        "remaining_chunks": after_count,
    }


def delete_all_vector_db_contents(batch_size: int = 1000) -> dict:
    """
    Deletes all chunks from the ChromaDB collection.
    This clears the knowledge base content but keeps the collection itself.
    """
    collection = get_vector_store_collection.get_vector_store_collection()

    all_ids = get_all_ids(batch_size=batch_size)

    if not all_ids:
        return {
            "status": "empty",
            "deleted_chunks": 0,
            "message": "ChromaDB is already empty."
        }

    for i in range(0, len(all_ids), batch_size):
        batch_ids = all_ids[i:i + batch_size]
        collection.delete(ids=batch_ids)

    return {
        "status": "success",
        "deleted_chunks": len(all_ids),
        "message": f"Deleted {len(all_ids)} chunks from ChromaDB."
    }