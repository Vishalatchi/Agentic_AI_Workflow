import os
from dotenv import load_dotenv

load_dotenv()

GROQ_AI_API_KEY= os.getenv("GROQ_AI_API_KEY")

if GROQ_AI_API_KEY is None:
    raise ValueError("API Key is not available")
