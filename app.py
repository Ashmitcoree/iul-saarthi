import json
import os

import streamlit as st

from agent import answer_question
from retrieval import load_documents, source_label


APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(APP_DIR, "data", "campus_faq.json")

st.set_page_config(
    page_title="IUL Saarthi | Campus Guide",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      :root {
        --saarthi-ink: #183b36;
        --saarthi-muted: #64736f;
        --saarthi-accent: #137c68;
        --saarthi-bg: #f5f8f7;
        --saarthi-border: #dce7e3;
      }
      .stApp { background: var(--saarthi-bg); }
      [data-testid="stHeader"] { background: rgba(245, 248, 247, 0.88); }
      [data-testid="stMainBlockContainer"] { max-width: 900px; padding-top: 2rem; }
      [data-testid="stSidebar"] { background: #edf4f1; border-right: 1px solid var(--saarthi-border); }
      .saarthi-hero {
        padding: 1.6rem 1.8rem 1.5rem;
        border: 1px solid var(--saarthi-border);
        border-radius: 22px;
        background: linear-gradient(130deg, #ffffff 5%, #e9f5f0 100%);
        box-shadow: 0 8px 28px rgba(24, 59, 54, 0.06);
        margin-bottom: 1rem;
      }
      .saarthi-kicker {
        color: var(--saarthi-accent); font-size: 0.76rem; font-weight: 750;
        letter-spacing: .12em; text-transform: uppercase; margin-bottom: .45rem;
      }
      .saarthi-title { color: var(--saarthi-ink); font-size: 2.35rem; font-weight: 780; line-height: 1.1; margin: 0; }
      .saarthi-subtitle { color: var(--saarthi-muted); font-size: 1.02rem; margin: .55rem 0 0; }
      .saarthi-badge {
        display: inline-flex; align-items: center; gap: .45rem; margin-top: 1rem;
        border: 1px solid #b9dfd3; border-radius: 999px; padding: .35rem .7rem;
        color: #17624f; background: #f1fbf7; font-size: .82rem; font-weight: 650;
      }
      .saarthi-section-label {
        color: var(--saarthi-muted); font-size: .82rem; font-weight: 700;
        letter-spacing: .06em; text-transform: uppercase; margin: 1.15rem 0 .25rem;
      }
      [data-testid="stChatMessage"] {
        border: 1px solid var(--saarthi-border); border-radius: 18px;
        padding: .55rem .8rem; background: rgba(255,255,255,.78);
      }
      [data-testid="stChatInput"] { border-color: #cbdcd6; }
      [data-testid="stChatInput"]:focus-within { border-color: var(--saarthi-accent); box-shadow: 0 0 0 2px rgba(19,124,104,.12); }
      [data-testid="stExpander"] { border-color: var(--saarthi-border); border-radius: 14px; background: #fff; }
      .evidence-text { color: #314b45; line-height: 1.55; font-size: .94rem; }
      @media (max-width: 640px) {
        .saarthi-hero { padding: 1.25rem; border-radius: 17px; }
        .saarthi-title { font-size: 1.9rem; }
        [data-testid="stMainBlockContainer"] { padding: 1rem .8rem 2rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

with open(DATA_PATH, "r", encoding="utf-8") as file:
    documents = load_documents(json.load(file))

st.markdown(
    """
    <section class="saarthi-hero">
      <div class="saarthi-kicker">Integral University · Student Support</div>
      <h1 class="saarthi-title">IUL Saarthi</h1>
      <p class="saarthi-subtitle">Campus answers grounded in the information available to the assistant.</p>
      <span class="saarthi-badge">✦ Gemma 4 E2B · running locally with Ollama</span>
    </section>
    """,
    unsafe_allow_html=True,
)

st.info(
    "**Prototype knowledge base:** team-provided Hack Day information only. "
    "This is a demo, not an official university service."
)

with st.sidebar:
    st.markdown("### About this demo")
    st.caption("IUL Saarthi searches its local knowledge base, checks for evidence, then asks Gemma to draft a grounded answer.")
    st.divider()
    st.markdown("**Local AI setup**")
    st.write("Gemma 4 E2B · Ollama")
    st.write(f"{len(documents)} information passages indexed")
    st.caption("Questions without supporting information receive a clear fallback.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("evidence"):
            with st.expander(f"Evidence used · {len(message['evidence'])} passage(s)"):
                for item in message["evidence"]:
                    st.markdown(f"**{source_label(item)}**")
                    st.markdown(f"<div class='evidence-text'>{item['text']}</div>", unsafe_allow_html=True)

st.markdown("<div class='saarthi-section-label'>Try a question</div>", unsafe_allow_html=True)
suggestions = [
    "Where is the Hack Day being held?",
    "What are the dates and schedule?",
    "How do I register?",
]
columns = st.columns(len(suggestions))
for index, (column, suggestion) in enumerate(zip(columns, suggestions)):
    with column:
        if st.button(suggestion, key=f"suggestion_{index}", use_container_width=True):
            st.session_state.pending_question = suggestion

question = st.chat_input("Ask about the Hack Day information")
if st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Checking the available information…"):
            result = answer_question(question, documents)
        st.markdown(result["answer"])
        evidence = result.get("evidence", [])
        if evidence:
            with st.expander(f"Evidence used · {len(evidence)} passage(s)", expanded=True):
                for item in evidence:
                    st.markdown(f"**{source_label(item)}**")
                    st.markdown(f"<div class='evidence-text'>{item['text']}</div>", unsafe_allow_html=True)
        if result.get("notice"):
            st.caption(result["notice"])
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "evidence": evidence,
        }
    )
