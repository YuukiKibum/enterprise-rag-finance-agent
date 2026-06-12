import streamlit as st
import os
import tempfile
import zipfile

from chroma_db_functionalities.ingest_files_to_vector_db import (
    ingest_document,
    ingest_folder
)

from chroma_db_functionalities.vector_db_inspection import (
    get_vector_db_summary,
    delete_document_from_vector_db,
    delete_all_vector_db_contents
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
    type=["pdf", "docx", "xlsx", "xls"],
    accept_multiple_files=True
)

if st.button("🚀 Ingest Files"):
    if not uploaded_files:
        st.warning("Please upload files first")
    else:
        success_results = []
        skipped_results = []
        failed_results = []

        with tempfile.TemporaryDirectory() as tmpdir:
            for file in uploaded_files:
                file_path = os.path.join(tmpdir, file.name)

                with open(file_path, "wb") as f:
                    f.write(file.read())

                try:
                    result = ingest_document(file_path)

                    if result["status"] == "success":
                        success_results.append(result)
                    else:
                        skipped_results.append(result)

                except Exception as e:
                    failed_results.append({
                        "file_name": file.name,
                        "reason": str(e)
                    })

        st.success(f"Ingestion completed. Successful files: {len(success_results)}")

        if success_results:
            st.subheader("✅ Successfully ingested")
            for item in success_results:
                st.write(
                    f"**{item['file_name']}** — {item['chunks']} chunks stored"
                )

        if skipped_results:
            st.subheader("⚠️ Skipped files")
            for item in skipped_results:
                st.write(
                    f"**{item['file_name']}** — {item.get('reason', 'Skipped')}"
                )

        if failed_results:
            st.subheader("❌ Failed files")
            for item in failed_results:
                st.write(
                    f"**{item['file_name']}** — {item['reason']}"
                )


# ---------------------------------------------------------
# FOLDER UPLOAD SECTION
# ---------------------------------------------------------
st.divider()
st.header("📁 Upload Folder as ZIP")

zip_file = st.file_uploader(
    "Upload ZIP folder. Subfolders are supported.",
    type=["zip"]
)

if st.button("🚀 Ingest Folder"):
    if not zip_file:
        st.warning("Please upload a ZIP file first")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "data.zip")

            with open(zip_path, "wb") as f:
                f.write(zip_file.read())

            extract_path = os.path.join(tmpdir, "extracted")
            os.makedirs(extract_path, exist_ok=True)

            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(extract_path)

                result = ingest_folder(extract_path)

                st.success(
                    f"Folder ingestion completed. "
                    f"Successful files: {len(result['successful'])}"
                )

                st.write(f"Total supported files found: {result['total_found']}")

                if result["successful"]:
                    st.subheader("✅ Successfully ingested")
                    for item in result["successful"]:
                        st.write(
                            f"**{item['file_name']}** — {item['chunks']} chunks stored"
                        )

                if result["skipped"]:
                    st.subheader("⚠️ Skipped files")
                    for item in result["skipped"]:
                        st.write(
                            f"**{item['file_name']}** — {item.get('reason', 'Skipped')}"
                        )

                if result["failed"]:
                    st.subheader("❌ Failed files")
                    for item in result["failed"]:
                        st.write(
                            f"**{item['file_name']}** — {item['reason']}"
                        )

            except zipfile.BadZipFile:
                st.error("Invalid ZIP file. Please upload a valid ZIP folder.")

# ---------------------------------------------------------
# DELETE / CLEAR CHROMADB SECTION
# ---------------------------------------------------------
st.divider()
st.header("🗑️ Manage ChromaDB Content")

summary = get_vector_db_summary()

st.write(f"**Total files in ChromaDB:** {summary['total_files']}")
st.write(f"**Total chunks in ChromaDB:** {summary['total_chunks']}")

if summary["total_files"] == 0:
    st.info("No files are currently stored in ChromaDB.")

else:
    st.subheader("Delete one file from ChromaDB")

    file_options = {
        f"{file['file_name']} — {file['chunk_count']} chunks": file["doc_id"]
        for file in summary["files"]
    }

    selected_file_label = st.selectbox(
        "Select file to delete",
        list(file_options.keys())
    )

    confirm_single_delete = st.checkbox(
        "I confirm I want to delete the selected file from ChromaDB"
    )

    if st.button("🗑️ Delete Selected File"):
        if not confirm_single_delete:
            st.warning("Please tick the confirmation checkbox first.")
        else:
            selected_doc_id = file_options[selected_file_label]
            result = delete_document_from_vector_db(selected_doc_id)

            st.success(
                f"Deleted selected file from ChromaDB. "
                f"Chunks deleted: {result['deleted_chunks']}"
            )

            st.rerun()


st.divider()
st.subheader("Danger Zone: Clear Entire ChromaDB")

st.warning(
    "This will delete ALL stored document chunks from ChromaDB. "
    "Your source files will not be deleted, only the vector database content."
)

confirm_text = st.text_input(
    "Type DELETE to confirm full ChromaDB deletion"
)

if st.button("🔥 Delete ALL ChromaDB Content"):
    if confirm_text != "DELETE":
        st.warning("Please type DELETE exactly to confirm.")
    else:
        result = delete_all_vector_db_contents()

        st.success(result["message"])

        st.rerun()
        
# ---------------------------------------------------------
# INFO SECTION
# ---------------------------------------------------------
st.divider()
st.info("""
✔ Supports PDF, DOCX, Excel  
✔ Upload multiple files  
✔ Upload full folder as ZIP  
✔ Supports subfolders inside ZIP  
✔ Automatically chunks + embeds + stores in ChromaDB  
✔ Re-uploading the same file replaces old chunks instead of duplicating them  
""")