import sys
from pathlib import Path

# Streamlit puts /app/frontend on sys.path, not /app. Add the project root
# so `backend` is importable when this script runs from anywhere.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from backend.rag import answer

st.set_page_config(page_title="RAG Q&A", page_icon=":books:")
st.title("RAG Q&A")

question = st.text_input("Ask a question about your documents:", "")
top_k = st.slider("Top-K chunks", 1, 10, 5)

if st.button("Ask", type="primary", disabled=not question.strip()):
    with st.spinner("Thinking..."):
        try:
            data = answer(question, top_k=top_k)
        except Exception as e:
            st.error(f"Query failed: {e}")
            st.stop()

    st.subheader("Answer")
    st.write(data["answer"])

    st.subheader("Sources")
    for src in data["sources"]:
        with st.expander(f"{src['source']} — chunk {src['chunk_index']} (sim {src['similarity']:.3f})"):
            st.write(src["content"])
