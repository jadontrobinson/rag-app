# RAG Q&A App

FastAPI + Supabase pgvector + Groq (Llama 3.3 70B) + Voyage AI embeddings, with a Streamlit UI.

## Stack

- **Backend**: FastAPI (`/query`, `/health`)
- **Vector store**: Supabase Postgres + pgvector (1024-dim, cosine)
- **Embeddings**: Voyage AI `voyage-3`
- **LLM**: Groq `llama-3.3-70b-versatile` (free tier)
- **Frontend**: Streamlit
- **Ingestion**: `.txt`, `.md`, `.pdf`

## Setup

### 1. Install

```bash
cd ~/Desktop/rag-app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# fill in GROQ_API_KEY, VOYAGE_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY
```

Get keys from:
- Groq: https://console.groq.com/keys (free tier)
- Voyage: https://dash.voyageai.com/
- Supabase: project Settings → API (use the **service_role** key, not anon)

### 3. Set up Supabase

1. Create a project at https://supabase.com/
2. In the SQL editor, paste and run the contents of `supabase_schema.sql`
3. This creates the `documents` table, the ivfflat index, and the `match_documents` RPC

### 4. Ingest documents

```bash
python ingest.py path/to/doc.pdf path/to/notes.md
# or a whole directory
python ingest.py path/to/folder/
```

### 5. Run

```bash
streamlit run frontend/app.py
```

Open http://localhost:8501.

The Streamlit app imports `backend.rag.answer()` directly — no separate API process needed. If you want the FastAPI endpoint (for other clients), run it separately: `uvicorn backend.main:app --reload`.

## Deploy to Railway

Single process: Streamlit on Railway's `$PORT` calling the RAG logic in-process. No FastAPI / uvicorn at runtime.

1. Push this repo to GitHub.
2. Create a Railway project → **Deploy from GitHub repo** → pick this repo.
3. Railway auto-detects the `Dockerfile` and `railway.toml`.
4. In the service **Variables** tab, add:
   - `GROQ_API_KEY`
   - `VOYAGE_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
5. Settings → **Networking** → **Generate Domain** to get a public URL.
6. Ingest documents locally against the same Supabase project (the data lives in Supabase, not on Railway):
   ```bash
   python ingest.py path/to/docs/
   ```

Or use the Railway CLI to run ingestion against the deployed env:
```bash
railway run python ingest.py path/to/docs/
```

To split into separate services later (e.g., expose FastAPI publicly), deploy `backend/main.py` as its own Railway service with `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` and have Streamlit call it over HTTP.

## Notes

- The Voyage `voyage-3` model uses `input_type="document"` at ingest and `input_type="query"` at retrieval — both go through the same model but Voyage tunes the embedding for each role.
- Groq's OpenAI-compatible chat completions API is used for inference. Free tier has rate limits — see https://console.groq.com/docs/rate-limits.
- Chunking is a simple character-window split (1000 chars, 200 overlap). Swap in a smarter splitter (`tiktoken`, semantic chunking) if your corpus needs it.
- The ivfflat index uses `lists = 100`. For large corpora (>100K rows), tune `lists` to ~sqrt(rows) and re-create the index.
