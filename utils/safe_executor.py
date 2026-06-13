import os
import sqlite3
import threading


def execute_query(sql: str, db_path: str, max_rows: int = 100, timeout_seconds: int = 10) -> dict:
    if not os.path.exists(db_path):
        return {"error": f"Database file not found: {db_path}", "error_type": "config"}

    result = {}
    error_container = [None]

    def _run():
        conn = None
        try:
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql)

            columns = [desc[0] for desc in cursor.description]
            rows_data = cursor.fetchmany(max_rows + 1)

            truncated = len(rows_data) > max_rows
            rows = rows_data[:max_rows]

            result["columns"] = columns
            result["rows"] = [list(row) for row in rows]
            result["row_count"] = len(rows)
            result["truncated"] = truncated

        except sqlite3.OperationalError as e:
            error_container[0] = {"error": str(e), "error_type": "sqlite"}
        except Exception as e:
            error_container[0] = {"error": str(e), "error_type": "unknown"}
        finally:
            if conn:
                conn.close()

    thread = threading.Thread(target=_run)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)

    if thread.is_alive():
        return {"error": f"Query timed out after {timeout_seconds} seconds.", "error_type": "timeout"}

    if error_container[0]:
        return error_container[0]

    return result
