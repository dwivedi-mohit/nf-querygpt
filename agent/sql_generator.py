import os
import json
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.llm_client import call_llm


def _load_system_prompt() -> str:
    path = os.path.join(os.path.dirname(__file__), "..", "prompts", "system_prompt.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are a SQL generator for NikahForever. Generate only SELECT queries."


def generate_sql(user_question: str, schema_context: str) -> dict:
    if not user_question or not user_question.strip():
        return {
            "sql": "",
            "explanation": "Please ask a question about NikahForever data.",
            "confidence": 0,
        }

    system_prompt = _load_system_prompt()
    system_prompt = system_prompt.replace("{schema_context}", schema_context)

    try:
        result = call_llm(system_prompt, user_question.strip())
    except Exception as e:
        error_msg = str(e)
        print(f"[SQL Generator] LLM call failed: {error_msg[:200]}")
        raise RuntimeError(f"Could not generate SQL: {error_msg[:200]}")

    if not isinstance(result, dict):
        return {
            "sql": "",
            "explanation": "Could not understand the question. Please rephrase.",
            "confidence": 5,
        }

    result.setdefault("sql", "")
    result.setdefault("explanation", "")
    result.setdefault("confidence", 5)

    try:
        result["confidence"] = int(result["confidence"])
    except (ValueError, TypeError):
        result["confidence"] = 5

    result["confidence"] = max(1, min(10, result["confidence"]))

    return result
