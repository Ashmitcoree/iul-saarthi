import json
import os
import base64
import mimetypes
from datetime import date, datetime

import streamlit as st
import streamlit.components.v1 as components

from agent import AI_BACKEND, answer_question, read_notice_image
from retrieval import load_documents, source_label


APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(APP_DIR, "data", "campus_faq.json")
OFFICES_PATH = os.path.join(APP_DIR, "data", "campus_offices.json")
VOICE_COMPONENT_PATH = os.path.join(APP_DIR, "voice_component")
voice_tools = components.declare_component("iul_saarthi_voice", path=VOICE_COMPONENT_PATH)

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
      .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { color: var(--saarthi-ink) !important; }
      .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label { color: var(--saarthi-ink); }
      [data-testid="stHeader"] { background: rgba(245, 248, 247, 0.88); }
      [data-testid="stMainBlockContainer"] { max-width: 1080px; padding-top: 2rem; position: relative; z-index: 1; }
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
      .saarthi-title { color: #183b36 !important; font-size: 2.35rem; font-weight: 780; line-height: 1.1; margin: 0; }
      .saarthi-subtitle { color: var(--saarthi-muted); font-size: 1.02rem; margin: .55rem 0 0; }
      .saarthi-identity { display: flex; align-items: center; gap: 1rem; }
      .saarthi-logo { width: 66px; height: 66px; object-fit: contain; flex: 0 0 auto; }
      .saarthi-logo-fallback { width: 66px; height: 66px; display: grid; place-items: center; border-radius: 18px; background: #e4f3ee; font-size: 2rem; }
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
      [data-testid="stChatInput"] { border: 2px solid #91cabb !important; border-radius: 18px !important; background: #ffffff !important; box-shadow: 0 5px 20px rgba(19,124,104,.10); transition: border-color .18s ease, box-shadow .18s ease; }
      [data-testid="stChatInput"]:focus-within { border-color: var(--saarthi-accent) !important; box-shadow: 0 0 0 4px rgba(19,124,104,.16), 0 7px 24px rgba(19,124,104,.13); }
      [data-testid="stExpander"] { border-color: var(--saarthi-border); border-radius: 14px; background: #fff; }
      .stApp button[kind="secondary"], .stApp button[data-testid="stBaseButton-secondary"] {
        color: #183b36 !important; background: #ffffff !important; border: 1px solid #c8ddd6 !important;
        font-weight: 650 !important; min-height: 3.1rem;
      }
      .stApp button[kind="secondary"] *, .stApp button[data-testid="stBaseButton-secondary"] * { color: #183b36 !important; }
      .stApp button[kind="secondary"]:hover, .stApp button[data-testid="stBaseButton-secondary"]:hover {
        color: #104f43 !important; background: #e7f4ef !important; border-color: #75b9a5 !important;
      }
      [data-testid="stChatInput"] textarea { color: #183b36 !important; font-size: 1rem !important; min-height: 2.8rem !important; }
      [data-testid="stChatInput"] textarea::placeholder { color: #64736f !important; opacity: 1 !important; font-weight: 550; }
      [data-testid="stChatInputSubmitButton"] { background: #137c68 !important; color: #ffffff !important; border-radius: 12px !important; }
      [data-testid="stChatInputSubmitButton"]:hover { background: #105f51 !important; transform: translateY(-1px); }
      .evidence-text { color: #314b45; line-height: 1.55; font-size: .94rem; }
      .voice-note { color: var(--saarthi-muted); font-size: .84rem; margin-top: -.4rem; }
      .saarthi-watermark { position: fixed; width: min(54vw, 560px); height: min(54vw, 560px); left: 50%; top: 55%; transform: translate(-50%, -50%); background-position: center; background-repeat: no-repeat; background-size: contain; opacity: .035; filter: grayscale(1); pointer-events: none; z-index: 0; }
      [data-testid="stMetric"] { background: rgba(255,255,255,.82); border: 1px solid var(--saarthi-border); border-radius: 16px; padding: .8rem 1rem; box-shadow: 0 4px 16px rgba(24,59,54,.035); }
      [role="tablist"] { gap: .4rem; border-bottom: 1px solid var(--saarthi-border); }
      button[role="tab"] { border-radius: 12px 12px 0 0; padding: .65rem 1rem; }
      button[role="tab"][aria-selected="true"] { color: var(--saarthi-accent); background: #e8f4ef; }
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
with open(OFFICES_PATH, "r", encoding="utf-8") as file:
    office_data = json.load(file)

logo_markup = "<div class='saarthi-logo-fallback'>🎓</div>"
for logo_name in ("iul_logo.png", "iul_logo.svg", "iul_logo.jpg", "iul_logo.jpeg"):
    logo_path = os.path.join(APP_DIR, "assets", logo_name)
    if os.path.isfile(logo_path):
        mime_type = mimetypes.guess_type(logo_path)[0] or "image/png"
        with open(logo_path, "rb") as logo_file:
            encoded_logo = base64.b64encode(logo_file.read()).decode("ascii")
        logo_markup = f"<img class='saarthi-logo' alt='Integral University logo' src='data:{mime_type};base64,{encoded_logo}'>"
        break

st.markdown(
    f"""
    <section class="saarthi-hero">
      <div class="saarthi-identity">
        {logo_markup}
        <div>
          <div class="saarthi-kicker">Integral University · Student Support</div>
          <h1 class="saarthi-title">IUL Saarthi</h1>
        </div>
      </div>
      <p class="saarthi-subtitle">Campus answers grounded in the information available to the assistant.</p>
      <span class="saarthi-badge">✦ {"Hosted Gemma 4 · Google AI API" if AI_BACKEND == "gemma_api" else "Gemma 4 E2B · local Ollama"}</span>
    </section>
    """,
    unsafe_allow_html=True,
)

st.info(
    "**Prototype knowledge base:** team-provided Hack Day details plus short guides to official university pages. "
    "The checked dates are recorded by the project team, not updated automatically. "
    "It does not sync live notices or student records and is not an official university service."
)


def freshness_label(verified_on):
    if not verified_on:
        return "Team-provided information · not checked against a live university page"
    checked_date = datetime.strptime(verified_on, "%Y-%m-%d").date()
    age_days = (date.today() - checked_date).days
    formatted = checked_date.strftime("%d %b %Y").lstrip("0")
    if age_days <= 0:
        return f"Page checked {formatted}"
    if age_days <= 30:
        return f"Page checked {formatted} · {age_days} days ago"
    return f"Page checked {formatted} · please recheck the official page"


if logo_markup.startswith("<img"):
    logo_data_uri = logo_markup.split("src='", 1)[1].split("'", 1)[0]
    st.markdown(
        f"<div class='saarthi-watermark' style='background-image:url({logo_data_uri})' aria-hidden='true'></div>",
        unsafe_allow_html=True,
    )

with st.sidebar:
    st.markdown("### About this demo")
    st.caption("IUL Saarthi searches its campus information, checks for evidence, then asks Gemma to draft a grounded answer.")
    st.divider()
    st.markdown("**AI setup**")
    st.write("Hosted Gemma 4 · Google AI API" if AI_BACKEND == "gemma_api" else "Gemma 4 E2B · local Ollama")
    st.write(f"{len(documents)} information passages indexed")
    st.caption("Questions without supporting information receive a clear fallback.")
    reply_language = st.selectbox("Reply language", ["Auto", "English", "Hindi"], index=0)
    st.caption("Choose English or Hindi to set the voice input language. Auto follows the question language for text chat.")

def render_evidence(evidence):
    if evidence:
        with st.expander(f"Evidence used · {len(evidence)} passage(s)"):
            for item in evidence:
                st.markdown(f"**{source_label(item)}**")
                st.markdown(f"<div class='evidence-text'>{item['text']}</div>", unsafe_allow_html=True)
                st.caption(freshness_label(item.get("verified_on")))
                if item.get("url"):
                    st.markdown(f"[Open official source ↗]({item['url']})")


def render_feedback(message_index):
    feedback = st.radio(
        "Was this answer helpful?",
        ["👍 Yes", "👎 Not yet"],
        index=None,
        horizontal=True,
        key=f"feedback_{message_index}",
        label_visibility="collapsed",
    )
    if feedback:
        st.caption("Thanks—your response stays in this browser session only.")


def render_office_finder():
    st.markdown("### Find a campus office")
    st.caption("Choose a destination to see available location and contact details.")
    office_names = [office["name"] for office in office_data["offices"]]
    selected_office_name = st.selectbox(
        "Choose an office or campus destination",
        office_names,
        key="office_finder",
    )
    selected_office = next(office for office in office_data["offices"] if office["name"] == selected_office_name)
    with st.container(border=True):
        st.markdown(f"**Location:** {selected_office['location']}")
        st.write(selected_office["directions_note"])
        st.markdown(f"**Contact:** {selected_office['contact']}")
        map_column, source_column = st.columns(2)
        with map_column:
            st.link_button("Open campus map pin", office_data["campus_map_url"], use_container_width=True)
        with source_column:
            st.link_button("Official office information", selected_office["url"], use_container_width=True)
        st.caption(f"{freshness_label(office_data['verified_on'])} · map shows the general university campus.")


def render_notice_reader():
    st.markdown("### Turn a campus notice into next steps")
    st.caption(
        "Upload a clear notice photo. Saarthi reads it with the configured Gemma service and makes a checklist. "
        "The image is used for this analysis and is not added to the shared campus knowledge base."
    )
    if AI_BACKEND == "gemma_api":
        st.info("Cloud mode sends the uploaded image to Google’s Gemma API for processing. Use public notices; avoid images with private student information.")
    notice_image = st.file_uploader(
        "Choose a notice image",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=False,
        help="Use a clear, well-lit photo. PNG, JPG, and WebP images up to 8 MB are supported.",
        key="notice_image_upload",
    )
    if notice_image is not None:
        image_bytes = notice_image.getvalue()
        if len(image_bytes) > 8 * 1024 * 1024:
            st.error("That image is over 8 MB. Please choose a smaller image.")
        else:
            st.image(image_bytes, caption="Photo selected for this analysis", use_container_width=True)
            if st.button("Read notice and make checklist", type="primary", key="read_notice"):
                with st.spinner("Reading the image with Gemma…"):
                    notice_result = read_notice_image(image_bytes, notice_image.type or "image/jpeg", reply_language)
                if notice_result.get("error"):
                    st.error(
                        "I couldn’t read this image. Check that the configured Gemma service is available and supports image input, "
                        "then try a clear PNG, JPG, or WebP photo."
                    )
                    st.caption(notice_result["error"])
                elif notice_result["kind"] == "unrelated":
                    st.info("I couldn’t find a campus notice in this image. Try a university notice, poster, or form.")
                elif notice_result["kind"] == "unclear":
                    st.warning("I couldn’t reliably read this image. Try a sharper, brighter photo with the full notice visible.")
                    if notice_result.get("transcription"):
                        with st.expander("Text I could make out"):
                            st.text(notice_result["transcription"])
                else:
                    st.success("Notice read. Please compare the checklist with the original notice before acting.")
                    if notice_result.get("actions"):
                        st.markdown("**Your checklist**")
                        for item in notice_result["actions"]:
                            st.text(f"☐ {item['action']}")
                            st.caption("Source text from the photo:")
                            st.text(item["source_quote"])
                    else:
                        st.info("I read the notice, but couldn’t verify any clear action items from its text.")
                    if notice_result.get("unclear"):
                        st.markdown("**Please confirm these unclear details**")
                        for detail in notice_result["unclear"]:
                            st.text(f"• {detail}")
                    if notice_result.get("transcription"):
                        with st.expander("Text read from the image"):
                            st.text(notice_result["transcription"])
                    st.caption("The result is based only on this photo; it is not verified against a live university source.")


def render_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None

    for message_index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("evidence"):
                render_evidence(message["evidence"])
            if message["role"] == "assistant":
                voice_language = (
                    "hi-IN"
                    if reply_language == "Hindi"
                    or (
                        reply_language == "Auto"
                        and any("ऀ" <= char <= "ॿ" for char in message["content"])
                    )
                    else "en-IN"
                )
                voice_tools(
                    mode="speak",
                    text=message["content"],
                    language=voice_language,
                    key=f"speak_answer_{message_index}",
                    default=None,
                )
                render_feedback(message_index)

    st.markdown("<div class='saarthi-section-label'>Try a question</div>", unsafe_allow_html=True)
    suggestions = (
        ["हैक डे कहाँ होगा?", "कार्यक्रम की तारीख और समय क्या है?", "मैं पंजीकरण कैसे करूँ?"]
        if reply_language == "Hindi"
        else ["Where is the Hack Day being held?", "What are the dates and schedule?", "How do I register?"]
    )
    columns = st.columns(len(suggestions))
    for index, (column, suggestion) in enumerate(zip(columns, suggestions)):
        with column:
            if st.button(suggestion, key=f"suggestion_{index}", use_container_width=True):
                st.session_state.pending_question = suggestion

    voice_result = voice_tools(
        mode="listen",
        language=("hi-IN" if reply_language == "Hindi" else "en-IN"),
        key="voice_question_input",
        default=None,
    )
    if isinstance(voice_result, dict) and voice_result.get("text"):
        if voice_result.get("id") != st.session_state.get("last_voice_id"):
            st.session_state.last_voice_id = voice_result.get("id")
            st.session_state.voice_draft = {
                "id": voice_result.get("id"),
                "text": voice_result["text"].strip(),
            }
    st.markdown(
        "<div class='voice-note'>Voice input uses your browser’s speech service after you tap the microphone. "
        "IUL Saarthi does not save audio. You can type instead.</div>",
        unsafe_allow_html=True,
    )

    voice_question = None
    if st.session_state.get("voice_draft"):
        draft = st.session_state.voice_draft
        with st.form(f"voice_review_{draft['id']}"):
            edited_transcript = st.text_input(
                "Review or edit what I heard",
                value=draft["text"],
                key=f"voice_review_text_{draft['id']}",
            )
            ask_column, discard_column = st.columns(2)
            with ask_column:
                ask_voice = st.form_submit_button("Ask Saarthi", type="primary", use_container_width=True)
            with discard_column:
                discard_voice = st.form_submit_button("Discard", use_container_width=True)
        if ask_voice and edited_transcript.strip():
            voice_question = edited_transcript.strip()
            st.session_state.voice_draft = None
        elif discard_voice:
            st.session_state.voice_draft = None

    st.markdown("<div class='saarthi-section-label'>Ask your campus question</div>", unsafe_allow_html=True)
    question = st.chat_input(
        "अपना विश्वविद्यालय-संबंधित सवाल यहाँ लिखें…"
        if reply_language == "Hindi"
        else "Type your campus question here…"
    )
    if not question:
        question = voice_question
    if st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Checking the available information…"):
                result = answer_question(question, documents, reply_language)
            st.markdown(result["answer"])
            evidence = result.get("evidence", [])
            render_evidence(evidence)
            if result.get("notice"):
                st.caption(result["notice"])
            render_feedback(len(st.session_state.messages))
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["answer"],
                "evidence": evidence,
            }
        )


metrics = st.columns(3)
with metrics[0]:
    st.metric("Campus information", f"{len(documents)} passages")
with metrics[1]:
    st.metric("Languages", "English · हिन्दी")
with metrics[2]:
    st.metric("Student tools", "3", help="Ask questions, read notices, or find campus offices.")

chat_tab, notice_tab, office_tab = st.tabs(
    ["💬 Ask Saarthi", "📰 Notice reader", "📍 Office finder"]
)
with chat_tab:
    st.caption("Ask a question by typing or voice. Answers include the evidence Saarthi used.")
    render_chat()
with notice_tab:
    render_notice_reader()
with office_tab:
    render_office_finder()