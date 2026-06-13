import pandas as pd


def format_results(execution_result: dict, explanation: str, sql: str) -> dict:
    if "error" in execution_result:
        return {
            "type": "error",
            "data": {
                "message": execution_result["error"],
                "error_type": execution_result.get("error_type", "unknown"),
            },
        }

    columns = execution_result.get("columns", [])
    rows = execution_result.get("rows", [])
    row_count = execution_result.get("row_count", 0)
    truncated = execution_result.get("truncated", False)

    if row_count == 0:
        return {
            "type": "success",
            "data": {
                "explanation": explanation,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "truncated": False,
                "sql": sql,
                "chart_type": None,
            },
        }

    chart_type = _detect_chart_type(columns, rows)

    return {
        "type": "success",
        "data": {
            "explanation": explanation,
            "columns": columns,
            "rows": rows,
            "row_count": row_count,
            "truncated": truncated,
            "sql": sql,
            "chart_type": chart_type,
        },
    }


def _detect_chart_type(columns: list, rows: list) -> str | None:
    col_lower = [c.lower() for c in columns]

    has_date = any(
        kw in c for kw in ["date", "month", "year", "day", "time", "created_at", "sent_at", "viewed_at", "matched_at"]
        for c in col_lower
    )

    numeric_cols = 0
    for row in rows[:5]:
        for val in row:
            if isinstance(val, (int, float)):
                numeric_cols += 1
                break

    if has_date and numeric_cols > 0:
        return "line"

    if len(columns) >= 2 and numeric_cols > 0:
        return "bar"

    return None
