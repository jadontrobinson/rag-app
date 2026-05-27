#!/usr/bin/env bash
set -e

# FastAPI on localhost only — Streamlit talks to it via RAG_API_URL.
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Streamlit binds to Railway's $PORT (public).
streamlit run frontend/app.py \
  --server.port=${PORT:-8501} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false &
FRONTEND_PID=$!

# Exit if either process dies so Railway restarts the container.
wait -n $BACKEND_PID $FRONTEND_PID
EXIT_CODE=$?
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
exit $EXIT_CODE
