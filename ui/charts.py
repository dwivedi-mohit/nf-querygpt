import streamlit as st
import plotly.express as px


PRIMARY_COLOR = "#8B5CF6"


def render_bar_chart(data, x_col: str, y_col: str, title: str = ""):
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        title=title,
        color_discrete_sequence=[PRIMARY_COLOR],
        text_auto=True,
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        hovermode="x",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def render_line_chart(data, x_col: str, y_col: str, title: str = ""):
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
        title=title,
        markers=True,
        color_discrete_sequence=[PRIMARY_COLOR],
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        hovermode="x",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def auto_chart(data, columns: list) -> str | None:
    col_lower = [c.lower() for c in columns]
    has_date = any(
        kw in c for kw in ["date", "month", "year", "day", "time", "created_at", "sent_at", "viewed_at", "matched_at"]
        for c in col_lower
    )
    has_numeric = any(data[c].dtype in ("int64", "float64") for c in columns)
    if has_date and has_numeric:
        return "line"
    if len(columns) >= 2 and has_numeric:
        return "bar"
    return None


def render_chart(data, chart_type: str | None = None):
    if chart_type is None:
        chart_type = auto_chart(data, data.columns.tolist())
    if chart_type is None:
        return

    columns = data.columns.tolist()
    numeric_cols = [c for c in columns if data[c].dtype in ("int64", "float64")]
    cat_cols = [c for c in columns if c not in numeric_cols]

    if chart_type == "bar" and cat_cols and numeric_cols:
        render_bar_chart(data, cat_cols[0], numeric_cols[0], f"{numeric_cols[0]} by {cat_cols[0]}")
    elif chart_type == "line" and len(columns) >= 2:
        date_col = next((c for c in columns if any(kw in c.lower() for kw in ["date", "month", "year", "day", "time", "created_at", "sent_at", "viewed_at", "matched_at"])), columns[0])
        y_col = numeric_cols[0] if numeric_cols else columns[-1]
        render_line_chart(data, date_col, y_col, f"{y_col} over time")
