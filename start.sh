#!/usr/bin/env bash
set -e

# Single process. Streamlit imports backend.rag.answer() directly — no HTTP hop.
exec streamlit run frontend/app.py \
  --server.port=${PORT:-8501} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --browser.gatherUsageStats=false
