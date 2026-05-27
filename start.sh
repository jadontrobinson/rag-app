#!/usr/bin/env bash
set -eu

# Railway injects $PORT. Fail loudly if it's missing or empty so the logs
# explain why instead of silently binding 8501 (which Railway can't reach).
if [[ -z "${PORT:-}" ]]; then
  echo "FATAL: \$PORT is not set. Railway must inject it." >&2
  exit 1
fi

echo "Starting Streamlit on 0.0.0.0:${PORT}"
exec python -m streamlit run frontend/app.py --server.port="${PORT}"
