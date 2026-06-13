# Technical Architecture Document: NF QueryGPT

**Version:** 1.0
**Project:** Build With TRAE Hackathon — Track 4
**Date:** June 13, 2026
**Status:** Final

---

## 1. Recommended Tech Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **UI Framework** | Streamlit | ≥1.28 | Fastest path to chat UI. Built-in `st.chat_message`, native charting (`st.bar_chart`, `st.line_chart`), zero frontend build step |
| **Primary LLM** | Groq (llama-3.3-70b-versatile) | — | 500+ tok/s inference. Free tier: 30 req/min, 14,400 req/day. Excellent at SQL generation |
| **Fallback LLM** | OpenRouter (gpt-4o-mini) | — | If Groq rate-limited. Single API key covers fallback. $0.15/M input tokens |
| **Orchestration** | Custom (no framework) | — | SQL gen is a single LLM call + regex validation. LangChain adds unnecessary latency and abstraction |
| **Database** | SQLite (Python `sqlite3`) | 3.x | Zero setup. 2.1 MB file, 40K records. Built-in module |
| **Query Validation** | Regex + sqlparse AST | — | Blocklist for INSERT/UPDATE/DELETE/DROP/ALTER. AST confirms SELECT-only |
| **Charts** | Plotly Express | 5.x | Interactive charts for aggregative queries |
| **Environment** | `.env` + python-dotenv | — | API keys, DB path, model name. No secrets in code |
| **Hinglish Support** | Prompt engineering only | — | 5 few-shot examples in system prompt. No separate NLP pipeline |
| **Package Manager** | pip + requirements.txt | — | Universal. No Docker needed |

### Rejected Alternatives

| Technology | Reason for Rejection |
|------------|---------------------|
| LangChain SQL Agent | Agent loop adds 2-3 extra LLM calls per query. Not needed for 12-table schema |
| LlamaIndex NLSQLTableQueryEngine | Same abstraction overhead. Judges want to see *our* logic, not framework's |
| Django/Flask | No backend needed. Streamlit runs Python directly |
| React/Next.js | Not buildable in 6 hours for a data app |
| Docker | Overhead for single-file demo |
| PostgreSQL | SQLite is faster for single-user, zero-config |

---

## 2. Complete File & Folder Structure

```
nf-querygpt/
│
├── app.py                          # Main entry point — Streamlit chat UI
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (API keys, config)
├── .gitignore                      # Git ignore rules
│
├── database/
│   ├── nf_buildathon.db            # SQLite database (2.1 MB)
│   └── schema.sql                  # Reference schema for prompt injection
│
├── agent/
│   ├── __init__.py
│   ├── orchestrator.py             # Main pipeline: classify → generate → validate → execute → format
│   ├── sql_generator.py            # LLM prompt construction & API call to Groq/OpenRouter
│   ├── validator.py                # Read-only enforcement (regex + AST check)
│   ├── clarifier.py                # Ambiguity detection & clarifying question generation
│   └── schema_context.py           # Builds schema description string for prompt injection
│
├── api/
│   ├── __init__.py
│   ├── llm_client.py               # Unified LLM client (Groq primary, OpenRouter fallback)
│   └── circuit_breaker.py          # Rate-limit handling, retry, graceful degradation
│
├── ui/
│   ├── __init__.py
│   ├── chat.py                     # Chat message rendering, suggestion chips, input handling
│   ├── results.py                  # Table display, number display, SQL reveal expander
│   └── charts.py                   # Chart selection & Plotly rendering logic
│
├── utils/
│   ├── __init__.py
│   ├── safe_executor.py            # SQLite query execution with timeout & row limits
│   └── formatter.py                # Formats results into natural language response
│
└── prompts/
    ├── system_prompt.txt           # Main system prompt with schema + rules + Hinglish examples
    ├── ambiguity_prompt.txt        # Prompt for ambiguity detection pass
    └── clarification_prompt.txt    # Prompt for generating clarifying questions
```

---

## 3. Database Schema

### Entity-Relationship Overview

```
Users ──┬── Profiles (1:1)
        ├── Partner_Preferences (1:1)
        ├── Subscriptions (1:N) ── Plans (N:1)
        ├── Payments (1:N)
        ├── Interests_Sent (1:N)
        ├── Interests_Received (1:N)
        ├── Support_Tickets (1:N)
        ├── Reports_Filed (1:N)
        └── Reports_Received (1:N)

Matches ──┬── Interest (N:1)
          └── Messages (1:N)

Profile_Views ──┬── Viewer (N:1)
                └── Viewed (N:1)
```

### 3.1 `users` — Core User Table (2,000 rows)

Central entity. Every other table references `user_id`.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `user_id` | INTEGER PK | No | — | Auto-increment unique identifier |
| `full_name` | TEXT | No | — | User's full name |
| `gender` | TEXT | No | — | `Male` or `Female` |
| `dob` | DATE | No | — | Date of birth |
| `phone` | TEXT | Yes | — | Synthetic Indian phone number |
| `email` | TEXT | Yes | — | Email address |
| `city` | TEXT | Yes | — | City of residence |
| `state` | TEXT | Yes | — | State of residence |
| `sect` | TEXT | Yes | — | Religious sect: `Sunni`, `Shia`, `Other`, `Prefer not to say` |
| `mother_tongue` | TEXT | Yes | — | Native language |
| `education_level` | TEXT | Yes | — | `High School`, `Bachelors`, `Masters`, `Doctorate` |
| `profession` | TEXT | Yes | — | Occupation |
| `annual_income_inr` | INTEGER | Yes | — | Annual income. NULL = not disclosed |
| `marital_status` | TEXT | Yes | — | `Never Married`, `Divorced`, `Widowed` |
| `managed_by` | TEXT | Yes | — | `Self`, `Parent`, `Sibling` |
| `is_verified` | INTEGER | No | `0` | Profile verified? 0=no, 1=yes |
| `account_status` | TEXT | No | — | `active`, `deactivated`, `suspended` |
| `created_at` | DATETIME | No | — | Account creation timestamp |
| `last_active_at` | DATETIME | Yes | — | Last activity timestamp |

**Business rules:**
- `gender` is binary (Male/Female)
- `annual_income_inr` NULL = not disclosed
- `account_status` = 'suspended' blocks all activity

### 3.2 `profiles` — Extended Profile (2,000 rows)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `profile_id` | INTEGER PK | No | Auto-increment |
| `user_id` | INTEGER FK (UNIQUE) | No | References `users(user_id)` |
| `bio` | TEXT | Yes | Free-text bio |
| `height_cm` | INTEGER | Yes | Height in cm |
| `photo_count` | INTEGER | No | Number of photos (default 0) |
| `profile_completeness_pct` | INTEGER | No | 0-100 derived completeness score |

### 3.3 `partner_preferences` — Match Preferences (2,000 rows)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `user_id` | INTEGER PK/FK | No | References `users(user_id)` |
| `min_age` | INTEGER | Yes | Minimum age of preferred partner |
| `max_age` | INTEGER | Yes | Maximum age of preferred partner |
| `preferred_sect` | TEXT | Yes | `Any` or specific sect |
| `min_education` | TEXT | Yes | Minimum education level |
| `preferred_cities` | TEXT | Yes | Comma-separated city names (denormalized) |

### 3.4 `plans` — Subscription Plans (3 rows)

| Column | Type | Description |
|--------|------|-------------|
| `plan_id` | INTEGER PK | 1=Silver, 2=Gold, 3=Platinum |
| `plan_name` | TEXT | Display name |
| `price_inr` | INTEGER | Price (999, 2499, 4999) |
| `duration_days` | INTEGER | Duration (30, 90, 180) |
| `contact_credits` | INTEGER | Credits (20, 75, 200) |

### 3.5 `subscriptions` — User Subscriptions (1,030 rows)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `subscription_id` | INTEGER PK | No | Auto-increment |
| `user_id` | INTEGER FK | No | References `users(user_id)` |
| `plan_id` | INTEGER FK | No | References `plans(plan_id)` |
| `start_date` | DATE | No | Subscription start |
| `end_date` | DATE | No | Subscription expiry |
| `status` | TEXT | No | `active`, `expired`, `cancelled` |
| `auto_renew` | INTEGER | No | 0=off, 1=on |

### 3.6 `payments` — Payment Transactions (1,288 rows)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `payment_id` | INTEGER PK | No | Auto-increment |
| `user_id` | INTEGER FK | No | References `users(user_id)` |
| `subscription_id` | INTEGER FK | Yes | References `subscriptions(subscription_id)` |
| `amount_inr` | INTEGER | No | Payment amount |
| `method` | TEXT | No | `UPI`, `Card`, `NetBanking`, `Wallet` |
| `status` | TEXT | No | `success`, `failed`, `refunded` |
| `created_at` | DATETIME | No | Payment timestamp |

### 3.7 `interests` — Interest Expressions (6,491 rows)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `interest_id` | INTEGER PK | No | Auto-increment |
| `sender_id` | INTEGER FK | No | User who sent the interest |
| `receiver_id` | INTEGER FK | No | User who received the interest |
| `sent_at` | DATETIME | No | When interest was sent |
| `status` | TEXT | No | `pending`, `accepted`, `declined` |
| `responded_at` | DATETIME | Yes | When receiver responded |

### 3.8 `matches` — Successful Matches (1,982 rows)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `match_id` | INTEGER PK | No | Auto-increment |
| `user_a_id` | INTEGER FK | No | Lower user_id (convention: user_a < user_b) |
| `user_b_id` | INTEGER FK | No | Higher user_id |
| `matched_at` | DATETIME | No | Match creation timestamp |
| `source_interest_id` | INTEGER FK | Yes | The interest that led to this match |

### 3.9 `messages` — Chat Messages (16,349 rows)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `message_id` | INTEGER PK | No | — | Auto-increment |
| `match_id` | INTEGER FK | No | — | References `matches(match_id)` |
| `sender_id` | INTEGER FK | No | — | Who sent the message |
| `sent_at` | DATETIME | No | — | Message timestamp |
| `is_read` | INTEGER | No | 0 | 0=unread, 1=read |

### 3.10 `profile_views` — Profile View Tracking (8,559 rows)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `view_id` | INTEGER PK | No | Auto-increment |
| `viewer_id` | INTEGER FK | No | User who viewed |
| `viewed_id` | INTEGER FK | No | User whose profile was viewed |
| `viewed_at` | DATETIME | No | View timestamp |

### 3.11 `reports` — Abuse Reports (259 rows)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `report_id` | INTEGER PK | No | Auto-increment |
| `reporter_id` | INTEGER FK | No | User filing the report |
| `reported_id` | INTEGER FK | No | User being reported |
| `reason` | TEXT | No | `fake profile`, `harassment`, `asking for money`, `inappropriate content`, `spam` |
| `created_at` | DATETIME | No | Report timestamp |
| `status` | TEXT | No | `open`, `actioned`, `dismissed` |
| `resolved_at` | DATETIME | Yes | Resolution timestamp |

### 3.12 `support_tickets` — Customer Support (500 rows)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `ticket_id` | INTEGER PK | No | Auto-increment |
| `user_id` | INTEGER FK | No | User who raised the ticket |
| `category` | TEXT | No | `payment`, `refund`, `profile_edit`, `verification`, `abuse`, `other` |
| `created_at` | DATETIME | No | Ticket creation |
| `status` | TEXT | No | `open`, `resolved`, `closed` |
| `resolved_at` | DATETIME | Yes | Resolution timestamp |
| `csat_score` | INTEGER | Yes | Customer satisfaction 1-5 |

---

## 4. Data Flow Architecture

```
                    ┌─────────────────────────────────────┐
                    │         Streamlit Frontend           │
                    │  (app.py)                           │
                    │  ┌─────────┐  ┌──────────────────┐  │
                    │  │ Chat UI │  │ Suggestion Chips  │  │
                    │  └────┬────┘  └──────────────────┘  │
                    └───────┼─────────────────────────────┘
                            │ user question
                            ▼
                    ┌─────────────────────────────────────┐
                    │         orchestrator.py              │
                    │  Step 1: Schema Injection           │
                    │  Step 2: Ambiguity Check            │
                    │    ├── Clear → Step 3               │
                    │    └── Ambiguous → return question  │
                    │  Step 3: SQL Generation (LLM)       │
                    │  Step 4: Safety Validation          │
                    │    ├── Pass → Step 5                │
                    │    └── Fail → return error          │
                    │  Step 5: Execute SQL (SQLite)       │
                    │  Step 6: Format Response            │
                    │  Step 7: Render (table/chart/text)  │
                    └─────────────────────────────────────┘
                            │
                    ┌───────┴────────┐
                    │                │
                    ▼                ▼
            ┌──────────────┐  ┌──────────────┐
            │  Groq API    │  │  SQLite DB   │
            │ (LLM call)   │  │ (read-only)  │
            └──────────────┘  └──────────────┘
```

---

## 5. Environment Variables & Configuration

### `.env` file

```bash
# ── LLM Provider ──
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MAX_TOKENS=1024
GROQ_TEMPERATURE=0.1

# ── Fallback LLM ──
OPENROUTER_API_KEY=sk-or-v1-your_key_here
OPENROUTER_MODEL=gpt-4o-mini
OPENROUTER_FALLBACK_ENABLED=true

# ── Database ──
DB_PATH=database/nf_buildathon.db

# ── Query Limits ──
MAX_ROWS_RETURNED=100
QUERY_TIMEOUT_SECONDS=10

# ── Ambiguity Threshold (1-10) ──
AMBIGUITY_THRESHOLD=7

# ── Logging ──
LOG_LEVEL=INFO

# ── App Config ──
APP_TITLE=NF QueryGPT
APP_DESCRIPTION="Ask anything about NikahForever data in plain English or Hinglish"
```

### Configuration Constants (for `config.py`)

```python
BLOCKED_SQL_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "TRUNCATE", "REPLACE", "CREATE", "GRANT", "REVOKE",
    "EXEC", "EXECUTE", "ATTACH", "DETACH", "VACUUM",
]

ALLOWED_STATEMENT_TYPES = ["SELECT", "WITH", "EXPLAIN"]

HINGLISH_EXAMPLES = [
    {"question": "Lucknow mein kitni women registered hain?",
     "sql": "SELECT COUNT(*) FROM users WHERE gender='Female' AND city='Lucknow'"},
    {"question": "Sabse zyada matches kis city mein hue?",
     "sql": "SELECT city, COUNT(*) as match_count FROM matches m JOIN users u ON m.user_a_id=u.user_id OR m.user_b_id=u.user_id GROUP BY city ORDER BY match_count DESC LIMIT 5"},
    {"question": "Mujhe active subscriptions dikhao",
     "sql": "SELECT u.full_name, p.plan_name, s.end_date FROM subscriptions s JOIN users u ON s.user_id=u.user_id JOIN plans p ON s.plan_id=p.plan_id WHERE s.status='active'"},
]
```

---

## 6. Key Architectural Decisions (ADRs)

### ADR-1: Custom orchestrator over LangChain

**Decision:** Write a 50-line orchestrator instead of using LangChain SQL Agent.
**Rationale:** LangChain's SQL agent loops cost 2-3 extra LLM calls per query. Single-shot prompt with few-shot examples achieves >90% accuracy for a 12-table schema.
**Trade-off:** Lost query correction loop. Mitigation: retry once with error message if SQL fails.

### ADR-2: Dual-pass ambiguity detection

**Decision:** Ask LLM to output `confidence` score (1-10) alongside SQL. If <7, trigger clarifying question.
**Rationale:** Simpler than training a classifier. LLM already understands underspecified queries.
**Trade-off:** Adds ~50 tokens per query. Negligible cost.

### ADR-3: SQL validation with regex + AST

**Decision:** Two-layer safety — regex keyword blocklist + `sqlparse` AST verification for SELECT-only.
**Rationale:** Regex alone can be bypassed (case variation). AST catches obfuscated SQL.
**Trade-off:** Adds one dependency (`sqlparse`). Worth the safety guarantee.

### ADR-4: Single-session, no persistence

**Decision:** No user auth, no chat history storage.
**Rationale:** MVP is a demo tool. Judges evaluate a single walkthrough. Auth/history = zero value for judging.

---

## 7. Performance & Scalability Notes

| Concern | Assessment |
|---------|-----------|
| **LLM latency** | Groq 300-500 tok/s → SQL generation in 1-2s |
| **SQLite query speed** | 40K records = sub-10ms for indexed queries |
| **Concurrent users** | None for MVP. Streamlit single-threaded |
| **Memory** | DB is 2.1 MB. App fits in <200 MB RAM |
| **API rate limits** | Groq: 30 req/min free. Fallback to OpenRouter |

---

## 8. Prerequisites Checklist

- [ ] Python 3.10+ installed
- [ ] Groq API key (console.groq.com)
- [ ] OpenRouter API key (openrouter.ai — optional fallback)
- [ ] Database file at `database/nf_buildathon.db`
- [ ] `requirements.txt` with: `streamlit`, `groq`, `openai`, `python-dotenv`, `sqlparse`, `plotly`
