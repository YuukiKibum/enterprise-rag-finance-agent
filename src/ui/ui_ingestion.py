import streamlit as st
import os
import tempfile
import zipfile

from chroma_db_functionalities.ingest_files_to_vector_db import (
    ingest_document,
    ingest_folder
)

st.set_page_config(page_title="Vector DB Ingestion", layout="centered")

st.title("📚 Serco Vector DB Ingestion UI")
st.write("Upload files or folders to ingest into ChromaDB")

# ---------------------------------------------------------
# FILE UPLOAD SECTION
# ---------------------------------------------------------
st.header("📄 Upload Files")

uploaded_files = st.file_uploader(
    "Upload PDF / DOCX / Excel files",
    type=["pdf", "docx", "xlsx"],
    accept_multiple_files=True
)

if st.button("🚀 Ingest Files"):
    if not uploaded_files:
        st.warning("Please upload files first")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            for file in uploaded_files:
                file_path = os.path.join(tmpdir, file.name)

                with open(file_path, "wb") as f:
                    f.write(file.read())

                ingest_document(file_path)

            st.success(f"Ingested {len(uploaded_files)} files successfully!")

# ---------------------------------------------------------
# FOLDER UPLOAD (ZIP for subfolders)
# ---------------------------------------------------------
st.divider()
st.header("📁 Upload Folder (ZIP)")

zip_file = st.file_uploader("Upload ZIP folder (supports subfolders)", type=["zip"])

if st.button("🚀 Ingest Folder"):
    if not zip_file:
        st.warning("Please upload a ZIP file first")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:

            zip_path = os.path.join(tmpdir, "data.zip")

            # Save zip
            with open(zip_path, "wb") as f:
                f.write(zip_file.read())

            extract_path = os.path.join(tmpdir, "extracted")
            os.makedirs(extract_path, exist_ok=True)

            # Extract ZIP
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)

            # Ingest entire folder (including subfolders)
            ingest_folder(extract_path)

            st.success("Folder ingested successfully!")

# ---------------------------------------------------------
# INFO SECTION
# ---------------------------------------------------------
st.divider()
st.info("""
✔ Supports PDF, DOCX, Excel  
✔ Upload multiple files  
✔ Upload full folder (ZIP) with subfolders  
✔ Automatically chunks + embeds + stores in vector DB  
""")