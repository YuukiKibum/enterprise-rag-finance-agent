from typing import List       # Helps define list types for clarity

from dotenv import load_dotenv        # Loads environment variables from .env file
from openai import OpenAI             # OpenAI client for embeddings


# ---------------------------------------------------------
#                 ENVIRONMENT + CLIENT SETUP
# ---------------------------------------------------------

load_dotenv()                 # Loads your .env file so OPENAI_API_KEY becomes available

openai_client = OpenAI()      # Creates a reusable OpenAI client for embeddings
# ---------------------------------------------------------
#                 EMBEDDING FUNCTION
# ---------------------------------------------------------

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Sends a list of text chunks to OpenAI and returns embeddings.
    Each embedding is a list of floating‑point numbers.
    """
    resp = openai_client.embeddings.create(
        model="text-embedding-3-small",  # Fast + cheap + high quality
        input=texts
    )

    # Extract the embedding vector from each response item
    return [d.embedding for d in resp.data]