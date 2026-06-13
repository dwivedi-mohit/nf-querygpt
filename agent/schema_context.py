import sqlite3
import os


def build_schema_context(db_path: str) -> str:
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    sections = []

    for table in tables:
        cursor.execute(f"PRAGMA table_info(\"{table}\")")
        columns = cursor.fetchall()

        col_lines = []
        for col in columns:
            cid, name, ctype, notnull, default, pk = col
            parts = [f"  - {name} ({ctype})"]
            if pk:
                parts.append("PK")
            if notnull:
                parts.append("NOT NULL")
            if default is not None:
                parts.append(f"default={default}")
            col_lines.append(" ".join(parts))

        cursor.execute(f"PRAGMA foreign_key_list(\"{table}\")")
        fks = cursor.fetchall()
        fk_lines = []
        for fk in fks:
            if len(fk) >= 9:
                id, seq, table_from, col_from, table_to, col_to, on_update, on_delete, match = fk
            else:
                id, seq, table_from, col_from, table_to, col_to, on_update, on_delete = fk
            fk_lines.append(f"  - FK: {col_from} -> {table_to}({col_to})")

        cursor.execute(f"SELECT * FROM \"{table}\" LIMIT 2")
        rows = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) FROM \"{table}\"")
        row_count = cursor.fetchone()[0]

        sample_rows_lines = []
        if rows:
            header = " | ".join([col[1] for col in columns])
            separator = " | ".join(["---"] * len(columns))
            sample_rows_lines.append(f"  {header}")
            sample_rows_lines.append(f"  {separator}")
            for row in rows:
                vals = [str(v) if v is not None else "NULL" for v in row]
                sample_rows_lines.append(" | ".join(vals))

        section = f"### {table} ({row_count} rows)"
        section += "\n" + "\n".join(col_lines)
        if fk_lines:
            section += "\n" + "\n".join(fk_lines)
        section += "\n" + "  Sample rows:"
        section += "\n" + "\n".join(sample_rows_lines)

        sections.append(section)

    conn.close()

    return "\n\n".join(sections)
