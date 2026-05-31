import os                     # Gives access to file paths, folder listing, etc.
from docx import Document     # Allows reading .docx Word files
import fitz                   # PyMuPDF Allows reading .pdf files
import pandas as pd           # Pandas: Used for reading, processing, and manipulating Excel files and tabular data

# ---------------------------------------------------------
#                 DOCUMENT LOADING FUNCTIONS
# ---------------------------------------------------------

def load_docx(path: str) -> str:
    """
    Reads a .docx Word file and extracts all text.
    Returns the full text as a single string.
    """
    doc = Document(path)

    paragraphs = [
        p.text.strip()
        for p in doc.paragraphs
        if p.text.strip()
    ]

    return "\n\n".join(paragraphs)


def load_pdf(path: str) -> str:
    """
    Reads a PDF file and extracts text from all pages.
    Returns the full text as a single string.
    """
    pdf = fitz.open(path)

    text = []

    for page in pdf:
        page_text = page.get_text().strip()

        if page_text:
            text.append(page_text)

    pdf.close()

    return "\n\n".join(text)

def load_excel(path: str) -> str:
    """
    Reads an Excel file (.xlsx) and converts all sheets into text.
    Each sheet is flattened into a readable string format.
    """

    excel_file = pd.ExcelFile(path)

    all_text = []

    for sheet_name in excel_file.sheet_names:
        df = excel_file.parse(sheet_name)

        # Convert dataframe to string (clean + structured)
        sheet_text = f"\n\n[Sheet: {sheet_name}]\n"

        # Fill NaN and convert everything to string
        df = df.fillna("")

        sheet_text += "\n".join(
                [
                    " | ".join(map(str, row))
                    for row in df.values
                ]
            )

        all_text.append(sheet_text)

    return "\n".join(all_text)


def load_file(path: str) -> str:
    """
    Detects the file type and loads it using the correct loader.
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".docx":
        return load_docx(path)

    elif ext == ".pdf":
        return load_pdf(path)
    
    elif ext in (".xlsx", ".xls"):
        return load_excel(path)

    raise ValueError(f"Unsupported file type: {ext}")