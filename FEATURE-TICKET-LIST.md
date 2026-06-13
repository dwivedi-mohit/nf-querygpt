# Feature Ticket List: NF QueryGPT

**Version:** 1.0
**Role:** Senior Engineering Lead
**Date:** June 13, 2026
**Project:** Build With TRAE Hackathon — Track 4

---

## Build Order Overview

The tickets are organized into **5 waves**, each building on the previous:

```
Wave 1: Foundation (Tickets 1-3) → project skeleton, DB, LLM client
Wave 2: Core Pipeline (Tickets 4-7) → SQL gen, validate, execute, clarify
Wave 3: Integration (Tickets 8-9) → orchestrator, chat UI
Wave 4: Polish (Tickets 10-12) → results, errors, suggestions
Wave 5: Enhancements (Tickets 13-15) → charts, Hinglish, circuit breaker
```

---

## Ticket 1 — Project Scaffold & Environment Setup

**Priority:** 🔴 Must-Have
**Dependencies:** None

### Description

Set up the Python project skeleton: folder structure, dependencies, environment variables, and a working Streamlit entry point that displays a placeholder page.

### Files to Create

- `requirements.txt`
- `.env` (template)
- `.gitignore`
- `app.py` (minimal Streamlit page with title and description)
- `database/` directory (copy `nf_buildathon.db` + `schema.sql`)
- `agent/__init__.py`, `api/__init__.py`, `ui/__init__.py`, `utils/__init__.py`

### Acceptance Criteria

- [ ] `pip install -r requirements.txt` completes without error
- [ ] `streamlit run app.py` launches a browser page with the app title "NF QueryGPT"
- [ ] `.env.template` exists with all required keys documented
- [ ] `nf_buildathon.db` is accessible via Python `sqlite3` module
- [ ] All empty `__init__.py` files exist at each package directory

### AI Prompt

> Create a Python Streamlit project for a natural-language-to-SQL app called NF QueryGPT. Set up requirements.txt with these dependencies: streamlit, groq, openai, python-dotenv, sqlparse, plotly. Create a minimal app.py that shows a centered title "NF QueryGPT" with subtitle "Ask anything about NikahForever data". Create these empty directories: agent/, api/, ui/, utils/, database/, prompts/. Create __init__.py in each subdirectory. Create a .env.template file with placeholders for GROQ_API_KEY, GROQ_MODEL, OPENROUTER_API_KEY, OPENROUTER_MODEL, DB_PATH, MAX_ROWS_RETURNED, QUERY_TIMEOUT_SECONDS, and AMBIGUITY_THRESHOLD. Copy the existing nf_buildathon.db and schema.sql into database/.

---

## Ticket 2 — Schema Context Builder

**Priority:** 🔴 Must-Have
**Dependencies:** Ticket 1

### Description

Build a module that reads the SQLite database schema and produces a formatted string describing all 12 tables, their columns, types, foreign keys, and 2 sample rows per table. This string is injected into the LLM system prompt so it knows the exact schema.

### Files to Create

- `agent/schema_context.py`

### Acceptance Criteria

- [ ] Returns a string containing all 12 table names with columns
- [ ] For each column: name, type, nullable status, foreign key reference
- [ ] Includes 2 sample rows per table as comma-separated values
- [ ] Output is formatted as markdown for easy injection
- [ ] Fails gracefully with clear error if DB file is missing

### AI Prompt

> Create a Python module at agent/schema_context.py. It should contain a function build_schema_context(db_path: str) -> str that connects to the given SQLite database, queries sqlite_master for all tables (excluding sqlite_*), and for each table builds a markdown-formatted string. For each table include: the table name, a list of columns (name, type, not null flag, default value, primary key flag), foreign key references, and 2 sample rows from the table. Use PRAGMA table_info and PRAGMA foreign_key_list to get metadata. The final output should be a string like: "### users\n- user_id (INTEGER) PK NOT NULL\n- full_name (TEXT) NOT NULL\n...\nSample rows:\n| user_id | full_name | ... |\n| 1 | Ayesha Hashmi | ... |". Handle the case where the database file doesn't exist with a clear FileNotFoundError.

---

## Ticket 3 — Unified LLM Client

**Priority:** 🔴 Must-Have
**Dependencies:** Ticket 1

### Description

Build a unified client that sends prompts to Groq (primary) and falls back to OpenRouter (secondary). Handle authentication, request formatting, and response parsing. Both APIs are OpenAI-compatible.

### Files to Create

- `api/llm_client.py`
- `api/circuit_breaker.py`

### Acceptance Criteria

- [ ] Calls Groq API with system + user messages and returns parsed content
- [ ] Falls back to OpenRouter if Groq returns 429 or 5xx
- [ ] Retries once after 2 seconds on failure before falling back
- [ ] Handles API key missing with clear error message
- [ ] Returns parsed JSON from LLM response
- [ ] Configurable model name, temperature, max_tokens via env vars

### AI Prompt

> Create two Python modules:
>
> **api/llm_client.py** — Contains a function call_llm(system_prompt: str, user_message: str, model: str | None = None) -> dict. It tries Groq first (using groq Python client), parses the response content as JSON, and returns it as a dict. If Groq fails with a rate limit (429) or server error (5xx), it falls back to OpenRouter (using openai Python client with base_url="https://openrouter.ai/api/v1"). Both use OpenAI-compatible chat completions endpoint. Read API keys and model names from environment variables (via python-dotenv). Temperature should be 0.1, max_tokens 1024. Return the parsed JSON object from the LLM's content field.
>
> **api/circuit_breaker.py** — Contains a wrapper function with_circuit_breaker(llm_func, *args, **kwargs) that implements: max 2 retries, 2-second delay between retries, fallback from Groq to OpenRouter on failure. Log all failures to print() with timestamp. If all retries fail, raise a clear RuntimeError with the underlying error message.

---

## Ticket 4 — SQL Generator

**Priority:** 🔴 Must-Have
**Dependencies:** Tickets 2, 3

### Description

Build the prompt construction and SQL generation module. Combines the schema context, system instructions, Hinglish few-shot examples, and the user's question into a prompt, then calls the LLM client to generate SQL.

### Files to Create

- `agent/sql_generator.py`
- `prompts/system_prompt.txt`
- `prompts/ambiguity_prompt.txt`

### Acceptance Criteria

- [ ] Constructs a system prompt with: role definition, safety rules, full schema context, Hinglish examples
- [ ] Calls LLM client with system + user message
- [ ] Parses LLM response as JSON: {sql, explanation, confidence}
- [ ] If LLM returns invalid JSON, retries once with error feedback
- [ ] Handles empty user input gracefully
- [ ] System prompt file is readable and editable without touching code

### AI Prompt

> Create agent/sql_generator.py with a function generate_sql(user_question: str, schema_context: str) -> dict that:
> 1. Loads the system prompt from prompts/system_prompt.txt (or a default string if file not found)
> 2. Injects the schema_context into the system prompt
> 3. Calls api/llm_client.call_llm(system_prompt, user_question)
> 4. Parses the response as JSON with keys: sql, explanation, confidence (integer 1-10)
> 5. If JSON parsing fails, retries once with error appended to user message
> 6. Returns the parsed dict
>
> Create prompts/system_prompt.txt with this content:
> "You are a SQL generator for NikahForever, an Indian matrimonial platform. Rules: 1. Generate ONLY SELECT queries. Never INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, REPLACE, CREATE. 2. Understand Hinglish queries — 'kitni' means 'how many', 'dikhao' means 'show', 'kaun sa' means 'which'. 3. If the question is ambiguous, set confidence below 7. 4. Never expose phone or email columns unless explicitly asked. 5. Limit results to 100 rows. 6. Use CURRENT_DATE and DATE functions for relative dates. 7. Respond ONLY with a JSON object: {\"sql\": \"...\", \"explanation\": \"...\", \"confidence\": <1-10>}. SCHEMA:\n{schema_context}\n\nHINGLISH EXAMPLES:\nQ: 'Lucknow mein kitni women registered hain?' → {\"sql\": \"SELECT COUNT(*) FROM users WHERE gender='Female' AND city='Lucknow'\", \"explanation\": \"Counts female users from Lucknow.\", \"confidence\": 9}\nQ: 'Sabse zyada matches kis city mein hue?' → {\"sql\": \"SELECT u.city, COUNT(*) as match_count FROM matches m JOIN users u ON m.user_a_id=u.user_id OR m.user_b_id=u.user_id GROUP BY u.city ORDER BY match_count DESC LIMIT 5\", \"explanation\": \"Finds top 5 cities with most matches.\", \"confidence\": 8}\nQ: 'Active subscriptions dikhao' → {\"sql\": \"SELECT u.full_name, p.plan_name, s.end_date FROM subscriptions s JOIN users u ON s.user_id=u.user_id JOIN plans p ON s.plan_id=p.plan_id WHERE s.status='active'\", \"explanation\": \"Lists users with active subscriptions.\", \"confidence\": 9}"
>
> Create prompts/ambiguity_prompt.txt with: "The user's question is ambiguous. Ask a clarifying question to narrow down what they mean. Do NOT generate SQL. Respond with a JSON object: {\"clarifying_question\": \"...\", \"options\": [\"...\", \"...\"]}"

---

## Ticket 5 — SQL Validator (Read-Only Enforcement)

**Priority:** 🔴 Must-Have
**Dependencies:** Ticket 1

### Description

Build a two-layer safety validator. Layer 1: regex keyword blocklist catches obvious write attempts. Layer 2: AST parser (sqlparse) confirms the statement type is SELECT/WITH/EXPLAIN. Block all other SQL.

### Files to Create

- `agent/validator.py`

### Acceptance Criteria

- [ ] Blocks SQL containing: INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, REPLACE, CREATE, GRANT, REVOKE, EXEC, ATTACH, DETACH, VACUUM (case-insensitive)
- [ ] Uses sqlparse to parse the SQL and verify the statement type is SELECT, WITH, or EXPLAIN
- [ ] Returns {"valid": True, "sql": sql} on pass
- [ ] Returns {"valid": False, "reason": "..."} on failure with specific reason
- [ ] Catches obfuscated SQL (e.g., "InSeRt" or "INSERT/*comment*/")
- [ ] Pure function — no external dependencies beyond sqlparse

### AI Prompt

> Create agent/validator.py with a function validate_sql(sql: str) -> dict. Two-layer validation:
>
> Layer 1 — Keyword check: Define a BLOCKED_KEYWORDS set with INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, REPLACE, CREATE, GRANT, REVOKE, EXEC, EXECUTE, ATTACH, DETACH, VACUUM. Normalize the SQL by removing string contents (replace anything between single quotes with '') and SQL comments (-- to end of line, /* */ blocks). Then check if any blocked keyword appears as a whole word (use regex \bkeyword\b with re.IGNORECASE). If blocked, return {"valid": False, "reason": "Query contains {keyword} which is not allowed. Only SELECT queries are permitted."}
>
> Layer 2 — AST check: Use sqlparse to parse the SQL. Extract the first statement's token type. If it's not a DML (SELECT) or CTE (WITH), return {"valid": False, "reason": "Only SELECT/WITH queries are allowed."}
>
> If both pass, return {"valid": True, "sql": sql}

---

## Ticket 6 — Safe SQLite Executor

**Priority:** 🔴 Must-Have
**Dependencies:** Ticket 1

### Description

Build a safe query executor that runs the validated SQL against SQLite with a timeout and row limit. Prevents long-running queries from hanging the app.

### Files to Create

- `utils/safe_executor.py`

### Acceptance Criteria

- [ ] Accepts validated SQL string and executes against SQLite
- [ ] Returns {columns, rows, row_count, truncated} structure
- [ ] Limits rows to MAX_ROWS_RETURNED from env (default 100)
- [ ] Kills query after QUERY_TIMEOUT_SECONDS (default 10)
- [ ] Handles SQLite errors (column not found, syntax error, etc.) with readable messages
- [ ] Does NOT commit any transactions (read-only connection)

### AI Prompt

> Create utils/safe_executor.py with a function execute_query(sql: str, db_path: str, max_rows: int = 100, timeout_seconds: int = 10) -> dict. Uses Python's sqlite3 module. Steps:
> 1. Connect to the database file at db_path (use check_same_thread=False for Streamlit)
> 2. Execute the SQL
> 3. Extract column names from cursor.description
> 4. Fetch up to max_rows + 1 rows (to detect truncation)
> 5. Set row_factory to sqlite3.Row for dict-like access
> 6. Return {"columns": [col_names], "rows": [list_of_lists], "row_count": len(rows), "truncated": len(rows) > max_rows}
> 7. For timeout, use Python's signal module (SIGALRM on Unix) or threading.Timer as fallback on Windows
> 8. On sqlite3.OperationalError, catch it and return {"error": str(e), "error_type": "sqlite"} instead of crashing
> 9. Ensure connection is closed in a finally block

---

## Ticket 7 — Ambiguity Clarifier

**Priority:** 🔴 Must-Have
**Dependencies:** Tickets 3, 4

### Description

Build the ambiguity detection module. When the LLM returns a confidence score below the threshold (default 7), this module generates a clarifying question to ask the user instead of running the query.

### Files to Create

- `agent/clarifier.py`
- `prompts/clarification_prompt.txt`

### Acceptance Criteria

- [ ] Takes user question + low-confidence LLM response
- [ ] Generates 1 clarifying question with 2-3 suggested answers
- [ ] Returns structured dict: {clarifying_question, options}
- [ ] Does NOT generate or execute any SQL
- [ ] Handles the case where the user's response to the clarification resolves the ambiguity
- [ ] Limits to 1 round of clarification (to avoid infinite loops)

### AI Prompt

> Create agent/clarifier.py with two functions:
>
> 1. ask_clarifying_question(user_question: str, original_llm_response: dict) -> dict: Loads the clarification prompt from prompts/clarification_prompt.txt, injects the user question and the LLM's low-confidence response, calls the LLM client, and returns the parsed response as {"clarifying_question": str, "options": [str, str, str]}
>
> 2. merge_clarification(original_question: str, clarification_answer: str) -> str: Combines the original question with the user's clarification into a single disambiguated question that can be re-sent to the SQL generator.
>
> Create prompts/clarification_prompt.txt: "The user asked: '{user_question}'. The AI was unsure and had low confidence (confidence score: {confidence}). Generate a single clarifying question that would disambiguate what the user wants. Provide 2-3 specific answer options the user can choose from. Respond as JSON: {\"clarifying_question\": \"...\", \"options\": [\"...\", \"...\", \"...\"]}. Do NOT generate any SQL."

---

## Ticket 8 — Main Orchestrator

**Priority:** 🔴 Must-Have
**Dependencies:** Tickets 4, 5, 6, 7

### Description

Build the central orchestrator that connects all agent modules into a single pipeline: schema → generate SQL → validate → (if ambiguous → clarify) → execute → format.

### Files to Create

- `agent/orchestrator.py`
- `utils/formatter.py`

### Acceptance Criteria

- [ ] Full pipeline executes in correct order: schema → generate → validate → execute → format
- [ ] If LLM confidence < threshold, triggers clarifier and waits for user response
- [ ] If SQL validation fails, returns user-friendly error without executing
- [ ] If SQLite execution fails (bad column, etc.), retries once with error feedback to LLM
- [ ] Returns structured result: {type, data, sql, explanation, error?}
- [ ] Handles all error types without crashing the app

### AI Prompt

> Create agent/orchestrator.py with a main function process_question(user_question: str, db_path: str, clarification_answer: str | None = None) -> dict. The pipeline:
> 1. Build schema context via schema_context.build_schema_context(db_path)
> 2. If clarification_answer is provided, merge it with original question via clarifier.merge_clarification()
> 3. Generate SQL via sql_generator.generate_sql(merged_question, schema_context)
> 4. If confidence < AMBIGUITY_THRESHOLD (from env), call clarifier.ask_clarifying_question() and return {"type": "clarify", "data": clarifying_response}
> 5. Validate SQL via validator.validate_sql(sql)
> 6. If validation fails, return {"type": "error", "data": validation_error}
> 7. Execute via safe_executor.execute_query(sql, db_path)
> 8. If execution returns error, retry once with error feedback (re-generate SQL with error appended), then if still fails return the error
> 9. Format results via formatter.format_results(execution_result, explanation, sql)
> 10. Return {"type": "success"|"error"|"clarify", "data": formatted_response}
>
> Create utils/formatter.py with format_results(execution_result: dict, explanation: str, sql: str) -> dict that structures the output into sections: {"explanation": str, "columns": list, "rows": list, "row_count": int, "truncated": bool, "sql": str, "chart_type": str|None}. Auto-detect chart_type: if results have a date column and a count, use "line"; if they have categorical data with counts, use "bar"; otherwise None.

---

## Ticket 9 — Chat UI (Streamlit)

**Priority:** 🔴 Must-Have
**Dependencies:** Tickets 1, 8

### Description

Build the Streamlit chat interface. Chat message rendering, input bar with submit, suggestion chips, and basic app layout (header, chat area, input bar fixed to bottom).

### Files to Create

- `ui/chat.py`
- Update `app.py` with full implementation

### Acceptance Criteria

- [ ] Chat input bar at bottom with send button
- [ ] User messages rendered as right-aligned purple bubbles
- [ ] AI messages rendered as left-aligned gray bubbles
- [ ] Loading indicator while processing (typing dots)
- [ ] Suggestion chips displayed on first load and after errors
- [ ] Header shows app name + subtitle
- [ ] Input disabled while processing

### AI Prompt

> Update app.py to implement a full Streamlit chat interface for NF QueryGPT. Use streamlit's chat elements (st.chat_message, st.chat_input). Layout:
> - Top: centered header with title "NF QueryGPT" and subtitle "Ask anything about NikahForever data in plain English or Hinglish". Use st.logo or st.image for a small icon.
> - Middle: scrollable chat area showing message history. Each message is a st.chat_message block. User messages use "user" avatar (right-aligned, purple). AI messages use "assistant" avatar (left-aligned, gray).
> - Bottom: st.chat_input with placeholder "Ask me about users, matches, subscriptions..."
> - On first load, show 3 suggestion chips as st.button or st.html: "How many users signed up this month?", "Show top 5 cities by female registrations", "Active subscriptions count"
> - When user submits: disable input, call orchestrator.process_question(), display result. Re-enable input when done.
> - Display loading state with st.spinner or a custom HTML typing indicator.
>
> Create ui/chat.py with helper functions:
> - render_user_message(text: str)
> - render_ai_message(response: dict) — calls results.py display functions
> - render_suggestion_chips(on_click_callback) — renders clickable suggestion chips
> - render_loading() — shows typing indicator

---

## Ticket 10 — Results Display (Tables, Numbers, SQL)

**Priority:** 🔴 Must-Have
**Dependencies:** Tickets 8, 9

### Description

Build the display components for query results. Supports plain numbers (COUNT, SUM), tables (SELECT multiple columns), and the collapsible SQL reveal.

### Files to Create

- `ui/results.py`

### Acceptance Criteria

- [ ] Single-number result displayed large and centered (e.g., "342")
- [ ] Table results displayed with headers, alternating rows, hover effect
- [ ] SQL shown in collapsible expander with dark code block styling
- [ ] Row count displayed ("Showing 100 of 1,284 results")
- [ ] Truncation notice shown if results exceed max rows
- [ ] Empty results show friendly message with suggestion chips

### AI Prompt

> Create ui/results.py with Streamlit display functions:
>
> 1. display_number_result(value: int, label: str) — Shows a large centered number with a label below it. Use st.metric or custom HTML with CSS. Style: font-size 48px, color #8B5CF6, bold.
>
> 2. display_table_result(columns: list, rows: list, row_count: int, truncated: bool) — Shows the data as a Streamlit dataframe with st.dataframe. Apply custom CSS: header background #F9FAFB, header text #6B7280 uppercase 11px, row hover #F9FAFB. If truncated, show "Showing {len(rows)} of {row_count} results" in a muted text below.
>
> 3. display_sql_block(sql: str) — Shows the SQL in a collapsible expander with label "Show SQL" / "Hide SQL". Inside, use a st.code block with language "sql" and background #1F2937. Add a small "Copy" button using st.button that copies the SQL to clipboard (use st.markdown with JavaScript or st.code with a copy icon).
>
> 4. display_empty_state() — Shows a centered message "No data matches your question" with suggestion chips below.
>
> 5. display_error_message(message: str, error_type: str) — Shows different styled alerts based on error_type: "blocked" → red, "timeout" → orange, "llm_error" → yellow, "no_results" → blue. Use st.error, st.warning, or st.info as appropriate.

---

## Ticket 11 — Charts & Visualizations

**Priority:** 🟡 Should-Have
**Dependencies:** Tickets 8, 10

### Description

Add chart visualization for aggregative queries. Bar charts for categorical comparisons, line charts for trends over time.

### Files to Create

- `ui/charts.py`

### Acceptance Criteria

- [ ] Bar chart auto-detected when result has categorical column + numeric column
- [ ] Line chart auto-detected when result has date column + numeric column
- [ ] Chart rendered below the table, interactive (hover tooltips)
- [ ] Chart type overridable by user request ("show me a chart" → auto-detect)
- [ ] Single-series charts (if one numeric column) colored primary purple
- [ ] Multi-series charts use the defined chart palette

### AI Prompt

> Create ui/charts.py with functions using Plotly Express (import plotly.express as px):
>
> 1. render_bar_chart(data: pd.DataFrame, x_col: str, y_col: str, title: str) — Renders an interactive bar chart with st.plotly_chart. Color: #8B5CF6. Show value labels on bars. Hover shows column name and value.
>
> 2. render_line_chart(data: pd.DataFrame, x_col: str, y_col: str, title: str) — Renders a line chart with markers. Color: #8B5CF6. X-axis dates formatted nicely. Hover shows date and value.
>
> 3. auto_chart(data: pd.DataFrame, columns: list) -> str | None — Analyzes the columns and returns "bar", "line", or None. Heuristic: if any column name contains "date", "month", "year", "day" → line chart. If columns have 2+ distinct values and a numeric column → bar chart. Otherwise None.
>
> 4. render_chart(data: pd.DataFrame, chart_type: str | None) — Main entry point. Calls auto_chart if chart_type is None, then renders the appropriate chart. Converts the result dict from executor into a pandas DataFrame first.

---

## Ticket 12 — Error Handling & Edge Cases

**Priority:** 🔴 Must-Have
**Dependencies:** Tickets 8, 9, 10

### Description

Implement comprehensive error handling across all failure points: LLM down, invalid SQL, query timeout, empty results, SQL injection attempts, missing config, etc.

### Files to Update

- `agent/orchestrator.py` (error handling paths)
- `ui/results.py` (error rendering)
- `app.py` (top-level error boundary)

### Acceptance Criteria

- [ ] LLM API down → shows "AI service busy" with retry suggestion
- [ ] Invalid SQL → shows specific error + suggests rephrasing
- [ ] Query timeout → shows "Query too slow" with narrowing suggestion
- [ ] No results → shows friendly empty state with suggestions
- [ ] SQL injection attempt → shows "Query blocked" message
- [ ] Missing .env → startup error with setup instructions
- [ ] Missing DB file → startup error with file path
- [ ] All errors show in plain language, no stack traces
- [ ] Loading state prevents double-submission

### AI Prompt

> Update these files to handle all error cases gracefully:
>
> In app.py: Wrap the entire orchestrator call in a try/except that catches RuntimeError (LLM failures), sqlite3.Error (DB issues), and generic Exception. Display each with the appropriate Streamlit error component. Add a safety check on app startup: verify .env exists (if not, show st.error with instructions), verify DB file exists (if not, show st.error with path). Disable the chat input button while a query is processing using a session state flag.
>
> In agent/orchestrator.py: Ensure every failure path returns a structured {"type": "error", "data": {"message": str, "error_type": str}} rather than raising exceptions to the UI. Map errors to types: "llm_error", "validation_error", "sql_error", "timeout_error", "no_results".
>
> In ui/results.py: Create a master render_response(response: dict) function that checks response["type"] and dispatches to the right renderer. Type "success" → display results. Type "clarify" → display clarifying question as an AI message with clickable option buttons. Type "error" → display_error_message.

---

## Ticket 13 — Hinglish Prompt Engineering

**Priority:** 🟡 Should-Have
**Dependencies:** Ticket 4

### Description

Enhance the system prompt with more comprehensive Hinglish support. Add 5-8 diverse Hinglish few-shot examples covering common query patterns.

### Files to Update

- `prompts/system_prompt.txt` (augment Hinglish examples section)
- `agent/sql_generator.py` (add Hinglish detection for routing)

### Acceptance Criteria

- [ ] Supports Hinglish queries for: counts, top-N, comparisons, filters by city/gender/status
- [ ] Mixed English-Hinglish queries work (e.g., "Mujhe active users dikhao from Delhi")
- [ ] Hindi numerals (e.g., "pichle mahine" = last month) map to SQL date functions
- [ ] All Hinglish examples produce valid SQL
- [ ] Base English queries still work (no regression)

### AI Prompt

> Update prompts/system_prompt.txt to expand the Hinglish examples section. Add these examples:
>
> Q: 'Pichle mahine kitne male users join hue?' → {"sql": "SELECT COUNT(*) FROM users WHERE gender='Male' AND created_at >= DATE('now', '-1 month')", "explanation": "Counts male users who joined last month.", "confidence": 9}
>
> Q: 'Mujhe top 10 cities dikhao with most profiles' → {"sql": "SELECT city, COUNT(*) as profile_count FROM users GROUP BY city ORDER BY profile_count DESC LIMIT 10", "explanation": "Shows top 10 cities with most user profiles.", "confidence": 9}
>
> Q: 'Kis state mein sabse zyada match hue?' → {"sql": "SELECT u.state, COUNT(*) as match_count FROM matches m JOIN users u ON m.user_a_id=u.user_id OR m.user_b_id=u.user_id GROUP BY u.state ORDER BY match_count DESC LIMIT 1", "explanation": "Finds the state with the most matches.", "confidence": 8}
>
> Q: 'Compare male vs female registrations this year' → {"sql": "SELECT gender, COUNT(*) as count FROM users WHERE strftime('%Y', created_at) = strftime('%Y', 'now') GROUP BY gender", "explanation": "Compares male vs female registrations this year.", "confidence": 9}
>
> Q: 'Kaun se users active nahi hain from past 3 months?' → {"sql": "SELECT full_name, city, last_active_at FROM users WHERE last_active_at IS NULL OR last_active_at < DATE('now', '-3 months') AND account_status='active'", "explanation": "Finds active accounts that haven't been active in 3+ months.", "confidence": 8}
>
> Add a note at the top of the system prompt: "The user may ask in Hinglish (Hindi + English mix). Common patterns: 'kitni'=how many, 'dikhao'=show, 'kaun sa'=which, 'mujhe'=show me, 'pichle mahine'=last month, 'kis'=which, 'wala/wali'=one that, 'mein'=in, 'hain'=are."

---

## Ticket 14 — Onboarding & Suggestion Chips

**Priority:** 🟡 Should-Have
**Dependencies:** Tickets 9, 10

### Description

Build the first-launch experience: welcome message, suggested questions, and context-setting so new users know what the app can do.

### Files to Update

- `ui/chat.py` (welcome message, chips)
- `app.py` (initial state handling)

### Acceptance Criteria

- [ ] First visit shows a welcome message from the AI explaining what it can do
- [ ] 4-6 suggestion chips appear below the welcome message
- [ ] Clicking a chip populates and submits the question
- [ ] After first query, suggestion chips hide (user knows how it works)
- [ ] Suggestion chips reappear if the user clears the chat or gets an error
- [ ] All suggestions are valid queries that return real data

### AI Prompt

> In app.py, add session state initialization: if 'chat_started' not in st.session_state, set it to False. On first load (chat_started is False), display a welcome AI message using st.chat_message("assistant") with text: "Hi! I'm NF QueryGPT. Ask me anything about NikahForever data — users, matches, subscriptions, payments, and more. I understand both English and Hinglish. Try one of these questions to get started:"
>
> Below the welcome message, render 6 suggestion chips using st.button in a horizontal layout (use st.columns with 3 columns, 2 rows, or use st.html with flexbox). Each chip is a small pill-button with text like:
> - "How many users are registered?"
> - "Show me active subscriptions"
> - "Top 5 cities by female users"
> - "How many matches this month?"
> - "Payment success rate?"
> - "Most common support ticket category"
>
> When a chip is clicked, set st.session_state.chat_started = True, set st.session_state.pending_question to the chip's text. In the main loop, if pending_question is set, auto-submit it and clear the flag.
>
> Update ui/chat.py to add render_welcome_message() and render_suggestion_chips() as described.

---

## Ticket 15 — Configuration & Startup Verification

**Priority:** 🟢 Nice-to-Have
**Dependencies:** Ticket 1

### Description

Build a startup verification routine that checks the environment is correctly configured before the app starts. Checks: .env exists, API keys are present, DB file exists, schema is valid, LLM API responds to a ping.

### Files to Create

- `utils/startup_checks.py`

### Acceptance Criteria

- [ ] Checks .env file exists at project root
- [ ] Checks GROQ_API_KEY is not empty
- [ ] Checks DB file exists at configured path
- [ ] Checks DB contains expected tables (at least users table)
- [ ] Optional: pings Groq API with a minimal request to verify key works
- [ ] Runs on app startup
- [ ] Fails fast with clear instructions for each failure mode

### AI Prompt

> Create utils/startup_checks.py with a function run_startup_checks() -> list[dict] that returns a list of check results. Each result is {"check": str, "passed": bool, "message": str}. Checks:
> 1. "env_file" — os.path.exists(".env") → if missing, message: "Create a .env file in the project root. Copy .env.template and fill in your API keys."
> 2. "groq_api_key" — os.getenv("GROQ_API_KEY") is set and not empty → if missing, message: "Set GROQ_API_KEY in .env. Get a key from console.groq.com."
> 3. "db_file" — os.path.exists(os.getenv("DB_PATH", "database/nf_buildathon.db")) → if missing, message: "Database file not found at {path}. Ensure nf_buildathon.db is in the database/ directory."
> 4. "db_tables" — connect to DB and check at least one table exists → if empty, message: "Database has no tables. Check that the database file is valid."
>
> At the end, return the full results list. In app.py, call run_startup_checks() on startup. If any check fails, display all failed checks as a list of st.error messages and stop execution with st.stop(). If all pass, show a small green st.success("All systems ready") that auto-fades.

---

## Dependency Graph

```
Ticket 1 ──┬── Ticket 2 ──┬── Ticket 4 ──┬── Ticket 8 ──┬── Ticket 9 ──┬── Ticket 10
           │              │               │              │              │
           │              │               │              │              ├── Ticket 11
           │              │               │              │              │
           │              │               │              │              └── Ticket 12
           │              │               │              │
           │              ├── Ticket 3 ───┘              │
           │              │                              ├── Ticket 13
           │              │                              │
           │              └── Ticket 7 ──────────────────┘
           │
           ├── Ticket 5 ─────────────────┘
           │
           ├── Ticket 6 ─────────────────┘
           │
           └── Ticket 15 (optional)
```

## Priority Summary

| Priority | Tickets | Total |
|----------|---------|-------|
| 🔴 Must-Have | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12 | 11 |
| 🟡 Should-Have | 11, 13, 14 | 3 |
| 🟢 Nice-to-Have | 15 | 1 |
| **Total** | | **15** |

---

## Build Sequence

| Wave | Tickets | Est. Time | What You Get |
|------|---------|-----------|-------------|
| **Wave 1** | 1, 2, 3 | ~45 min | Working skeleton, schema reader, LLM client |
| **Wave 2** | 4, 5, 6, 7 | ~60 min | Core pipeline — SQL gen, validate, execute, clarify |
| **Wave 3** | 8, 9 | ~45 min | Working app — orchestrator + chat UI |
| **Wave 4** | 10, 12 | ~40 min | Complete MVP — results display + error handling |
| **Wave 5** | 11, 13, 14, 15 | ~50 min | Polish — charts, Hinglish, onboarding, checks |
