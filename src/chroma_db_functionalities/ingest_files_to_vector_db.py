from . import get_vector_store_collection
from . import load_files
from . import smart_chunking
from . import create_embeddings
import os                      # Gives access to file paths, folder listing, etc.
import uuid                    # Used to generate unique IDs for each chunk
from dotenv import load_dotenv # Loads environment variables from .env file

load_dotenv() 

def ingest_document(path: str, doc_id: str | None = None):
    """
    Ingests ONE document into ChromaDB.
    Steps:
    1. Load text
    2. Smart chunking
    3. Embedding
    4. Add metadata
    5. Store in Chroma
    """
    collection = get_vector_store_collection.get_vector_store_collection()

    # If no doc_id provided, use the file path as the document ID
    doc_id = doc_id or path

    # 1) Load raw text from file
    full_text = load_files.load_file(path)

    # 2) Smart chunking (automatic chunking + overlap)
    chunks = smart_chunking.chunk_text_smart(full_text)

    if not chunks:
        print(f"No content found in {path}")
        return

    # 3) Embed all chunks
    embeddings = create_embeddings.embed_texts(chunks)

    # 4) Create unique IDs + metadata for each chunk
    ids = [str(uuid.uuid4()) for _ in chunks]

    metadatas = [
        {
            "doc_id": doc_id,                 # Logical document ID
            "file_name": os.path.basename(path),
            "chunk_index": i,                 # Which chunk number this is
            "total_chunks": len(chunks),      # Total chunks in this document
        }
        for i in range(len(chunks))
    ]

    # 5) Store everything in ChromaDB
    collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Ingested {len(chunks)} chunks from {path} (doc_id={doc_id})")


# ---------------------------------------------------------
#         INGEST ALL DOCUMENTS IN A FOLDER (NEW)
# ---------------------------------------------------------

def ingest_folder(folder_path: str):
    """
    Scans a folder and ingests ALL supported documents inside it.
    """
    supported_extensions = (".docx", ".pdf")

    for file_name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file_name)

        # Skip folders
        if os.path.isdir(full_path):
            continue

        # Only process supported file types
        if file_name.lower().endswith(supported_extensions):
            print(f"\nProcessing: {file_name}")
            ingest_document(full_path)
        else:
            print(f"Skipping unsupported file: {file_name}")

# ---------------------------------------------------------
#                 EXAMPLE USAGE
# ---------------------------------------------------------

if __name__ == "__main__":
    ingest_folder("serco_files")   # Ingest all .docx files in the folder