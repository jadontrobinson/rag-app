#!/usr/bin/env bash
set -e

# Backend: internal only. Streamlit reaches it via http://127.0.0.1:8000.
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &

# Frontend: bind to Railway's public $PORT. exec so Streamlit becomes PID 1 —
# signals propagate, and if it dies Railway restarts the container.
exec streamlit run frontend/app.py \
  --server.port=${PORT:-8501} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --browser.gatherUsageStats=false
