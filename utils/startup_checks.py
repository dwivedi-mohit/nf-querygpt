import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()


def run_startup_checks() -> list[dict]:
    results = []

    results.append(_check_env_file())
    results.append(_check_groq_api_key())
    results.append(_check_db_file())
    results.append(_check_db_tables())
    results.append(_check_db_path_env())

    return results


def _check_env_file() -> dict:
    exists = os.path.exists(".env")
    return {
        "check": "Environment file (.env)",
        "passed": exists,
        "message": "" if exists else "Create a .env file in the project root. Copy .env.template and fill in your API keys.",
    }


def _check_groq_api_key() -> dict:
    key = os.getenv("GROQ_API_KEY", "")
    passed = bool(key and key != "gsk_your_key_here")
    return {
        "check": "Groq API Key",
        "passed": passed,
        "message": "" if passed else "Set GROQ_API_KEY in .env. Get a key from console.groq.com.",
    }


def _check_db_path_env() -> dict:
    db_path = os.getenv("DB_PATH", "database/nf_buildathon.db")
    return {
        "check": "DB_PATH in .env",
        "passed": bool(db_path),
        "message": "" if db_path else "Set DB_PATH in .env to point to the SQLite database file.",
    }


def _check_db_file() -> dict:
    db_path = os.getenv("DB_PATH", "database/nf_buildathon.db")
    exists = os.path.exists(db_path)
    return {
        "check": "Database file",
        "passed": exists,
        "message": "" if exists else f"Database file not found at '{db_path}'. Ensure nf_buildathon.db exists.",
    }


def _check_db_tables() -> dict:
    db_path = os.getenv("DB_PATH", "database/nf_buildathon.db")
    if not os.path.exists(db_path):
        return {"check": "Database tables", "passed": False, "message": "Database file missing, cannot check tables."}
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        count = cursor.fetchone()[0]
        conn.close()
        passed = count > 0
        return {
            "check": "Database tables",
            "passed": passed,
            "message": "" if passed else "Database has no tables. Check that the database file is valid.",
        }
    except Exception as e:
        return {"check": "Database tables", "passed": False, "message": f"Could not read database: {str(e)[:100]}"}
