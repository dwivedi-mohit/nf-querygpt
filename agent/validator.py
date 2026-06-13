import re
import sqlparse


BLOCKED_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "TRUNCATE", "REPLACE", "CREATE", "GRANT", "REVOKE",
    "EXEC", "EXECUTE", "ATTACH", "DETACH", "VACUUM",
}


def _normalize_sql(sql: str) -> str:
    cleaned = re.sub(r"'[^']*'", "", sql)
    cleaned = re.sub(r"--[^\n]*", "", cleaned)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
    return cleaned


def _keyword_check(sql: str) -> str | None:
    normalized = _normalize_sql(sql)
    for keyword in BLOCKED_KEYWORDS:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, normalized, re.IGNORECASE):
            return keyword
    return None


def _ast_check(sql: str) -> bool:
    try:
        parsed = sqlparse.parse(sql)
        if not parsed:
            return False
        stmt = parsed[0]
        token_type = stmt.token_first(skip_cm=True)
        if token_type is None:
            return False
        ttype = token_type.ttype
        from sqlparse.tokens import DML, CTE
        return ttype in (DML, CTE) or token_type.value.upper() in ("SELECT", "WITH", "EXPLAIN")
    except Exception:
        return False


def validate_sql(sql: str) -> dict:
    if not sql or not sql.strip():
        return {"valid": False, "reason": "Empty SQL query."}

    blocked = _keyword_check(sql)
    if blocked:
        return {
            "valid": False,
            "reason": f"Query contains '{blocked}' which is not allowed. Only SELECT queries are permitted.",
        }

    if not _ast_check(sql):
        return {"valid": False, "reason": "Only SELECT/WITH queries are allowed."}

    return {"valid": True, "sql": sql}
