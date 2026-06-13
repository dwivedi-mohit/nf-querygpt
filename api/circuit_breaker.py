import time
from datetime import datetime


def with_circuit_breaker(llm_func, *args, **kwargs):
    max_retries = 2
    retry_delay = 2

    last_error = None

    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                print(f"[CircuitBreaker] Retry {attempt}/{max_retries} at {datetime.now().isoformat()}")
            return llm_func(*args, **kwargs)
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            is_rate_limit = "429" in error_str or "rate_limit" in error_str
            is_server_error = "503" in error_str or "502" in error_str or "500" in error_str

            if is_rate_limit:
                print(f"[CircuitBreaker] Rate limited (attempt {attempt + 1})")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                    continue
            elif is_server_error:
                print(f"[CircuitBreaker] Server error (attempt {attempt + 1})")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                    continue
            else:
                if attempt < max_retries:
                    print(f"[CircuitBreaker] Transient error: {str(e)[:100]} (attempt {attempt + 1})")
                    time.sleep(retry_delay)
                    continue
                raise RuntimeError(f"LLM call failed after {max_retries + 1} attempts: {str(e)[:200]}")

    raise RuntimeError(f"LLM call failed after {max_retries + 1} attempts: {str(last_error)[:200]}")
