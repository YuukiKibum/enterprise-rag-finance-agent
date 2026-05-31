from dotenv import load_dotenv
load_dotenv()

import os

OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL")