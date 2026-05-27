import os

import requests
import streamlit as st

API_URL = os.environ.get("RAG_API_URL", "http://localhost:8000")

st.set_page_config(page_title="RAG Q&A", page_icon=":books:")
st.title("RAG Q&A")
st.caption(f"Backend: {API_URL}")

question = st.text_input("Ask a question about your documents:", "")
top_k = st.slider("Top-K chunks", 1, 10, 5)

if st.button("Ask", type="primary", disabled=not question.strip()):
    with st.spinner("Thinking..."):
        try:
            resp = requests.post(
                f"{API_URL}/query",
                json={"question": question, "top_k": top_k},
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")
            st.stop()

    st.subheader("Answer")
    st.write(data["answer"])

    st.subheader("Sources")
    for src in data["sources"]:
        with st.expander(f"{src['source']} — chunk {src['chunk_index']} (sim {src['similarity']:.3f})"):
            st.write(src["content"])
