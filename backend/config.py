import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
VOYAGE_API_KEY = os.environ["VOYAGE_API_KEY"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

EMBEDDING_MODEL = "voyage-3"
EMBEDDING_DIM = 1024

ANSWER_MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 1024

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 5
