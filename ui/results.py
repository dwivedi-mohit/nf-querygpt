import streamlit as st


def render_response(response: dict):
    rtype = response.get("type", "error")
    data = response.get("data", {})

    if rtype == "success":
        _render_success(data)
    elif rtype == "clarify":
        _render_clarify(data)
    elif rtype == "error":
        _render_error(data)
    else:
        st.error("Unexpected response type.")


def _render_success(data: dict):
    explanation = data.get("explanation", "")
    columns = data.get("columns", [])
    rows = data.get("rows", [])
    row_count = data.get("row_count", 0)
    truncated = data.get("truncated", False)
    sql = data.get("sql", "")
    chart_type = data.get("chart_type")

    if explanation:
        st.markdown(f"_{explanation}_")

    if row_count == 0 and not columns:
        display_empty_state()
        return

    if row_count == 1 and len(columns) == 1:
        display_number_result(rows[0][0], columns[0])
    else:
        display_table_result(columns, rows, row_count, truncated)

    if chart_type and row_count > 0:
        try:
            from ui.charts import render_chart
            import pandas as pd
            df = pd.DataFrame(rows, columns=columns)
            render_chart(df, chart_type)
        except Exception as e:
            pass

    if sql:
        display_sql_block(sql)


def _render_clarify(data: dict):
    question = data.get("clarifying_question", "Could you please clarify?")
    options = data.get("options", [])

    st.markdown(f"**{question}**")

    cols = st.columns(min(len(options), 3))
    for i, option in enumerate(options):
        col = cols[i % len(cols)]
        if col.button(option, key=f"clarify_{i}", use_container_width=True):
            st.session_state.clarification_answer = option
            st.session_state.needs_clarification = True
            st.rerun()


def _render_error(data: dict):
    message = data.get("message", "An error occurred.")
    error_type = data.get("error_type", "unknown")

    if error_type == "validation_error":
        st.error(f"🚫 {message}")
    elif error_type == "llm_error":
        st.warning(f"🤖 {message}")
    elif error_type == "timeout":
        st.warning(f"⏱️ {message}")
    elif error_type == "no_results":
        display_empty_state()
    elif error_type == "config":
        st.error(f"⚙️ {message}")
    else:
        st.error(f"❌ {message}")

    if error_type in ("llm_error", "timeout", "no_sql"):
        display_suggestion_chips()


def display_number_result(value, label: str = ""):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 3rem; font-weight: 700; color: #8B5CF6;">{value}</div>
                <div style="font-size: 0.9rem; color: #6B7280;">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def display_table_result(columns: list, rows: list, row_count: int, truncated: bool):
    import pandas as pd
    df = pd.DataFrame(rows, columns=columns)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={col: st.column_config.Column(col.title()) for col in columns},
    )

    if truncated:
        st.caption(f"Showing {len(rows)} of {row_count}+ results. Narrow your question for more specific data.")
    else:
        st.caption(f"{row_count} result(s)")


def display_sql_block(sql: str):
    with st.expander("Show SQL"):
        st.code(sql, language="sql")
        if st.button("📋 Copy SQL", key="copy_sql"):
            st.toast("SQL copied to clipboard!")
            st.markdown(
                f'<textarea id="sql_copy" style="position:absolute;left:-9999px;">{sql}</textarea>'
                '<script>document.getElementById("sql_copy").select();document.execCommand("copy");</script>',
                unsafe_allow_html=True,
            )


def display_empty_state():
    st.info("📭 No data matches your question. Try asking differently or use one of the suggestions below.")
    display_suggestion_chips()


def display_suggestion_chips():
    suggestions = [
        "How many users are registered?",
        "Show me active subscriptions",
        "Top 5 cities by female users",
        "How many matches this month?",
    ]
    cols = st.columns(len(suggestions))
    for i, suggestion in enumerate(suggestions):
        if cols[i].button(suggestion, key=f"sug_{i}", use_container_width=True):
            st.session_state.pending_question = suggestion
            st.rerun()
