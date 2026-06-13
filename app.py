import streamlit as st
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from dotenv import load_dotenv

load_dotenv()

from agent.orchestrator import process_question
from ui.chat import render_welcome_message, render_suggestion_chips
from ui.results import render_response
from utils.startup_checks import run_startup_checks

st.set_page_config(
    page_title="NF QueryGPT",
    page_icon="💜",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .main-header { text-align: center; padding: 2rem 0 1rem 0; }
    .main-header h1 { color: #8B5CF6; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.3rem; }
    .main-header p { color: #6B7280; font-size: 1rem; }
    .stApp { padding-bottom: 80px; }
    .stChatInput { position: fixed; bottom: 0; left: 0; right: 0; background: white; padding: 1rem 2rem; border-top: 1px solid #E5E7EB; z-index: 100; }
    .block-container { max-width: 760px; padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

checks = run_startup_checks()
failed = [c for c in checks if not c["passed"]]
if failed:
    st.error("### Startup Checks Failed")
    for check in failed:
        st.error(f"**{check['check']}:** {check['message']}")
    st.stop()
else:
    st.success("All systems ready", icon="✅")

st.markdown('<div class="main-header"><h1>💜 NF QueryGPT</h1><p>Ask anything about NikahForever data in plain English or Hinglish</p></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None
if "processing" not in st.session_state:
    st.session_state.processing = False
if "clarification_answer" not in st.session_state:
    st.session_state.clarification_answer = None
if "needs_clarification" not in st.session_state:
    st.session_state.needs_clarification = False
if "awaiting_clarification" not in st.session_state:
    st.session_state.awaiting_clarification = False

DB_PATH = os.getenv("DB_PATH", "database/nf_buildathon.db")

if not st.session_state.chat_started and not st.session_state.messages:
    render_welcome_message()
    render_suggestion_chips()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        if isinstance(content, dict):
            render_response(content)
        else:
            st.markdown(content)

if st.session_state.pending_question:
    prompt = st.session_state.pending_question
    st.session_state.pending_question = None
    st.session_state.chat_started = True
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.processing = True
    st.rerun()

if st.session_state.needs_clarification and st.session_state.clarification_answer:
    answer = st.session_state.clarification_answer
    st.session_state.clarification_answer = None
    st.session_state.needs_clarification = False
    st.session_state.messages.append({"role": "user", "content": answer})
    st.session_state.processing = True
    st.session_state.awaiting_clarification = True
    st.rerun()

if st.session_state.processing:
    last_user_msg = None
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "user":
            last_user_msg = msg["content"]
            break

    if last_user_msg:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    clarification = None
                    if st.session_state.get("awaiting_clarification"):
                        clarification = last_user_msg
                        st.session_state.awaiting_clarification = False

                    response = process_question(
                        st.session_state.get("original_question", last_user_msg),
                        DB_PATH,
                        clarification,
                    )

                    rtype = response.get("type")

                    if rtype == "clarify":
                        st.session_state.original_question = st.session_state.get("original_question", last_user_msg)

                    render_response(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    err_msg = f"Something went wrong: {str(e)[:200]}"
                    st.error(err_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": {"type": "error", "data": {"message": err_msg, "error_type": "unknown"}},
                    })

    st.session_state.processing = False
    st.rerun()

chat_disabled = st.session_state.processing or st.session_state.needs_clarification
prompt = st.chat_input("Ask me about users, matches, subscriptions...", disabled=chat_disabled)
if prompt:
    st.session_state.chat_started = True
    st.session_state.original_question = prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.processing = True
    st.rerun()
