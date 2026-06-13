import os
import json
from dotenv import load_dotenv

load_dotenv()


def call_llm(system_prompt: str, user_message: str, model: str | None = None) -> dict:
    if model is None:
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    max_tokens = int(os.getenv("GROQ_MAX_TOKENS", "1024"))
    temperature = float(os.getenv("GROQ_TEMPERATURE", "0.1"))

    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set in .env file")

    try:
        from groq import Groq
        client = Groq(api_key=groq_api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as groq_error:
        error_str = str(groq_error)
        status_code = getattr(groq_error, "status_code", 0) or getattr(groq_error, "code", 0)

        is_rate_limit = status_code == 429 or "rate_limit" in error_str.lower()
        is_server_error = status_code >= 500 or status_code == 0

        fallback_enabled = os.getenv("OPENROUTER_FALLBACK_ENABLED", "true").lower() == "true"

        if (is_rate_limit or is_server_error) and fallback_enabled:
            return _fallback_to_openrouter(system_prompt, user_message, max_tokens, temperature)

        raise RuntimeError(f"LLM API error: {error_str}")


def _fallback_to_openrouter(system_prompt: str, user_message: str, max_tokens: int, temperature: float) -> dict:
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")

    if not api_key:
        raise RuntimeError("OpenRouter fallback enabled but OPENROUTER_API_KEY is not set")

    from openai import OpenAI
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    return json.loads(content)
