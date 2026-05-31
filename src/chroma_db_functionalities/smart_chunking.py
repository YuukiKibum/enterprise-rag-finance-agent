from typing import List                                             # Helps define list types for clarity
from langchain_text_splitters import RecursiveCharacterTextSplitter # Smart text splitter (modern RAG best practice)
                                                                    #Automatically handles chunking, overlap, and semantic boundaries

# ---------------------------------------------------------
#                 SMART CHUNKING (BEST PRACTICE)
# ---------------------------------------------------------

def chunk_text_smart(text: str) -> List[str]:
    """
    Uses RecursiveCharacterTextSplitter:
    - Splits by paragraphs → sentences → words → characters
    - Adds overlap automatically
    - Produces clean, semantic chunks
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # Ideal chunk size for RAG (not too big, not too small)
        chunk_overlap=200,    # Overlap preserves context between chunks
        length_function=len,  # How chunk size is measured (characters)
        separators=[
            "\n\n",           # Try splitting by paragraphs first
            "\n",             # Then by single newlines
            ". ",             # Then by sentences
            " ",              # Then by words
            ""                # Finally by characters (fallback)
        ],
    )

    return splitter.split_text(text)  # Returns a list of chunk strings