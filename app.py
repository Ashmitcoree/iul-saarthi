import json
import os
import urllib.error
import urllib.request

import streamlit as st

from agent import answer_question
from retrieval import load_documents


APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(APP_DIR, "data", "campus_faq.json")

st.set_page_config(page_title="IUL Saarthi", page_icon="🎓", layout="centered")
st.title("IUL Saarthi")
st.caption("A campus information assistant grounded in its available sources")
st.info(
    "Demo knowledge base: team-provided Hack Day information only. "
    "This is a prototype, not an official university service."
)

with open(DATA_PATH, "r", encoding="utf-8") as file:
    documents = load_documents(json.load(file))

with st.sidebar:
    st.subheader("Prototype setup")
    st.write("Model: Gemma 4 E2B")
    st.write("Runtime: Ollama on this computer")
    st.write(f"Indexed passages: {len(documents)}")
    st.caption("Answers are limited to the indexed information.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Sources"):
                for source in message["sources"]:
                    st.write(source)

question = st.chat_input("Ask about the Hack Day information")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the available information…"):
            result = answer_question(question, documents)
        st.markdown(result["answer"])
        if result["sources"]:
            with st.expander("Sources", expanded=True):
                for source in result["sources"]:
                    st.write(source)
        if result.get("notice"):
            st.caption(result["notice"])
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        }
    )

