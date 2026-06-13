import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.schema_context import build_schema_context
from agent.sql_generator import generate_sql
from agent.validator import validate_sql
from agent.clarifier import ask_clarifying_question, merge_clarification
from utils.safe_executor import execute_query
from utils.formatter import format_results


def process_question(user_question: str, db_path: str, clarification_answer: str | None = None) -> dict:
    try:
        schema_context = build_schema_context(db_path)
    except FileNotFoundError as e:
        return {"type": "error", "data": {"message": str(e), "error_type": "config"}}
    except Exception as e:
        return {"type": "error", "data": {"message": f"Schema error: {str(e)[:200]}", "error_type": "config"}}

    if clarification_answer:
        user_question = merge_clarification(user_question, clarification_answer)

    try:
        llm_result = generate_sql(user_question, schema_context)
    except RuntimeError as e:
        return {"type": "error", "data": {"message": str(e), "error_type": "llm_error"}}
    except Exception as e:
        return {"type": "error", "data": {"message": f"Unexpected LLM error: {str(e)[:200]}", "error_type": "llm_error"}}

    sql = llm_result.get("sql", "").strip()
    explanation = llm_result.get("explanation", "")
    confidence = llm_result.get("confidence", 5)

    if not sql:
        return {
            "type": "error",
            "data": {
                "message": "I couldn't generate a query from your question. Please rephrase with more detail.",
                "error_type": "no_sql",
            },
        }

    ambiguity_threshold = int(os.getenv("AMBIGUITY_THRESHOLD", "7"))
    if confidence < ambiguity_threshold:
        try:
            clarify_response = ask_clarifying_question(user_question, llm_result)
            return {"type": "clarify", "data": clarify_response}
        except Exception as e:
            return {"type": "error", "data": {"message": f"Could not process ambiguity: {str(e)[:200]}", "error_type": "clarify_error"}}

    validation = validate_sql(sql)
    if not validation["valid"]:
        return {"type": "error", "data": {"message": validation["reason"], "error_type": "validation_error"}}

    max_rows = int(os.getenv("MAX_ROWS_RETURNED", "100"))
    timeout = int(os.getenv("QUERY_TIMEOUT_SECONDS", "10"))

    execution_result = execute_query(sql, db_path, max_rows=max_rows, timeout_seconds=timeout)

    if "error" in execution_result:
        error_msg = execution_result["error"]
        error_type = execution_result.get("error_type", "sql_error")

        if error_type == "sqlite":
            retry_result = _retry_with_feedback(sql, error_msg, user_question, schema_context, max_rows, timeout)
            if retry_result:
                return retry_result

        return {"type": "error", "data": {"message": error_msg, "error_type": error_type}}

    return format_results(execution_result, explanation, sql)


def _retry_with_feedback(original_sql: str, error_msg: str, user_question: str, schema_context: str, max_rows: int, timeout: int) -> dict | None:
    try:
        feedback = f"Your previous SQL was: {original_sql}. It failed with error: {error_msg}. Fix the SQL."
        retry_result = generate_sql(f"{user_question} (Note: {feedback})", schema_context)
        retry_sql = retry_result.get("sql", "").strip()

        if not retry_sql:
            return None

        retry_validation = validate_sql(retry_sql)
        if not retry_validation["valid"]:
            return None

        redo = execute_query(retry_sql, "E:/trae/database/nf_buildathon.db", max_rows=max_rows, timeout_seconds=timeout)
        if "error" not in redo:
            return format_results(redo, retry_result.get("explanation", ""), retry_sql)
    except Exception:
        pass

    return None
