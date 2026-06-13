import streamlit as st


def render_welcome_message():
    with st.chat_message("assistant"):
        st.markdown(
            "Hi! I'm **NF QueryGPT**. Ask me anything about NikahForever data — "
            "users, matches, subscriptions, payments, and more. "
            "I understand both English and Hinglish. Try one of these questions to get started:"
        )


def render_suggestion_chips():
    suggestions = [
        "How many users are registered?",
        "Show me active subscriptions",
        "Top 5 cities by female users",
        "How many matches this month?",
        "Payment success rate?",
        "Most common support ticket category",
    ]

    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        col = cols[i % 3]
        if col.button(suggestion, key=f"welcome_sug_{i}", use_container_width=True):
            st.session_state.pending_question = suggestion
            st.rerun()


def render_user_message(text: str):
    with st.chat_message("user"):
        st.markdown(text)


def render_ai_message(response: dict):
    from ui.results import render_response
    with st.chat_message("assistant"):
        render_response(response)
