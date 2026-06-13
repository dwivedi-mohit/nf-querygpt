import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.llm_client import call_llm


def _load_clarification_prompt() -> str:
    path = os.path.join(os.path.dirname(__file__), "..", "prompts", "clarification_prompt.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "The user asked: '{user_question}'. Generate a clarifying question."


def ask_clarifying_question(user_question: str, original_llm_response: dict) -> dict:
    prompt_template = _load_clarification_prompt()
    confidence = original_llm_response.get("confidence", 5)
    prompt = prompt_template.replace("{user_question}", user_question)
    prompt = prompt.replace("{confidence}", str(confidence))

    result = call_llm(
        "You are a clarifying question generator for a SQL assistant.",
        prompt,
    )

    return {
        "clarifying_question": result.get("clarifying_question", "Could you please clarify?"),
        "options": result.get("options", ["Yes", "No"]),
    }


def merge_clarification(original_question: str, clarification_answer: str) -> str:
    return f"{original_question} ({clarification_answer})"
