# Product Requirements Document: NF QueryGPT

> **Product:** NF QueryGPT — AI-Powered Natural Language to SQL Assistant
> **Project:** Build With TRAE Hackathon
> **Date:** June 13, 2026
> **Track:** Track 4 — Data & Analytics
> **Status:** Draft v1.0

---

## 1. Product Overview

**NF QueryGPT** is an AI-powered natural language to SQL assistant for **NikahForever** — a matrimonial platform. It allows non-technical team members (product managers, customer support, operations) to ask business questions in plain English (or Hinglish) and get instant answers from the database, without writing a single SQL query or waiting on the data team.

---

## 2. Target Users

| Persona | Description | Pain Point |
|---------|-------------|-----------|
| **Priya (Product Manager)** | Needs daily user acquisition & engagement metrics | Currently submits Slack ticket to data team, waits 2-6 hours |
| **Rahul (Customer Support Lead)** | Investigates user complaints about matches, payments, profiles | Can't self-serve; escalates everything to engineering |
| **Anjali (Operations Manager)** | Tracks regional growth, drop-off funnel, and match success rate | Relies on stale dashboards that don't answer ad-hoc questions |
| **Vikas (Founder/CEO)** | Wants quick pulse checks before investor meetings | Has to ping the CTO for every number |

---

## 3. Problem Statement

**Data at NikahForever is locked behind SQL.** Business users have questions daily — *"How many women signed up from Lucknow this week?"*, *"Which age group has the highest match rate?"*, *"Show me profiles created but not verified in the last 7 days"* — but each question requires a data team member to interpret, write SQL, run it, and share results. This creates a **2-6 hour turnaround bottleneck**, demoralizes curious team members, and leaves business decisions data-poor.

**Our solution:** A chat interface where anyone types their question and gets an instant answer—with the SQL displayed for transparency, and guardrails to prevent any data corruption.

---

## 4. Core Features — Must-Have vs Nice-to-Have

### Must-Have (MVP — this is the hackathon deliverable)

| # | Feature | Rationale |
|---|---------|-----------|
| 1 | **Natural language → SQL conversion** (English + Hinglish) | Core value prop |
| 2 | **Read-only enforcement** — block INSERT/UPDATE/DELETE/DROP/ALTER | Non-negotiable safety |
| 3 | **Show generated SQL** in the response | Trust & transparency (judging criteria) |
| 4 | **Result display** — table (CSV-style) + numeric answer | Most common output |
| 5 | **Simple chart visualization** for aggregate data (bar chart for counts, line for trends) | Makes answers instantly scannable |
| 6 | **Ambiguity handling** — when the question is vague, ask a clarifying question instead of guessing | Prevents hallucinations (judging criteria) |
| 7 | **Schema context injection** — the LLM knows all 12 tables, columns, relationships, and sample values | Accurate SQL generation |
| 8 | **Streamlit or Gradio web UI** with a chat interface | Fastest path to working demo |
| 9 | **Error messages in plain language** — "I couldn't find a column called 'city'. Did you mean 'location_city'?" | UX polish |

### Nice-to-Have (post-MVP)

| # | Feature | Why defer |
|---|---------|-----------|
| 1 | **Chat history & session management** | Adds DB complexity; MVP is single-session |
| 2 | **Dashboard with saved queries** | Not needed for initial demonstration |
| 3 | **Multi-language support** beyond Hinglish (Tamil, Bengali) | MVP validates with English/Hinglish first |
| 4 | **Voice input** | Cool but adds failure modes; ship text first |
| 5 | **Export to PDF/CSV** | Requires backend processing; copy-paste works for MVP |
| 6 | **User authentication & role-based access** | Single-user demo mode is fine for submission |
| 7 | **Query caching for performance** | 40K records is small; SQLite handles it fine |
| 8 | **Feedback loop** ("Was this answer helpful?") | Nice for iteration, not for judging |

---

## 5. User Flow (End-to-End)

```
START
  │
  ▼
[1] User lands on chat UI
  │  Greeting: "Hi! Ask me anything about NikahForever data."
  │  Suggestion chips: "How many users signed up this month?"
  │                       "Show top 5 cities by female registrations"
  │
  ▼
[2] User types question (English or Hinglish)
  │  Example: "Lucknow mein kitni women registered hain?"
  │
  ▼
[3] System analyzes intent
  ├── If clear → proceed to SQL generation
  └── If ambiguous → ask clarifying question
       Example: "Do you mean total registered women from Lucknow,
                 or women registered *this month* from Lucknow?"
       User clarifies → loop back
  │
  ▼
[4] LLM generates SQL query
  │   SELECT COUNT(*) FROM users
  │   WHERE gender = 'female'
  │   AND city = 'Lucknow'
  │
  ▼
[5] Safety check: SQL passes read-only validation?
  ├── ✅ Pass → execute against nf_buildathon.db
  └── ❌ Fail → show error: "This query might modify data. Blocked."
  │
  ▼
[6] Execute query → get results
  │
  ▼
[7] Display response:
  │   "Total women registered from Lucknow: 342"
  │   [Table showing breakdown by month if relevant]
  │   [Bar chart if showing comparison]
  │   "Generated SQL: SELECT COUNT(*) FROM users ..." (collapsible)
  │
  ▼
[8] User asks follow-up or new question
  │
  ▼
[9] (Optional) "Show me a chart" or "Export these results"
  │
  └── Repeat from step 2
```

---

## 6. MVP Definition (Version 1.0)

**The MVP is a single-page chat application.** No auth, no history, no multi-session. One user opens the page, types questions, gets answers.

**Tech Stack:**
| Layer | Choice | Why |
|-------|--------|-----|
| **Frontend** | Streamlit (Python) | Fastest to build, built-in chat components, handles charts natively |
| **LLM** | Groq (Llama 3.3 70B) or OpenRouter (GPT-4o-mini or DeepSeek V4 Flash) | Fast inference, free tier, strong at SQL generation |
| **Database** | SQLite (nf_buildathon.db) | Already provided, zero setup |
| **Framework** | LangChain SQL Agent or LlamaIndex `NLSQLTableQueryEngine` | Production-tested text-to-SQL pipelines |
| **Charts** | Streamlit `st.bar_chart` + `st.line_chart` | Built-in, zero config |
| **Hosting** | Local demo (or Streamlit Community Cloud if needed) | No deployment complexity |

**Files:**
```
nf-querygpt/
├── app.py                 # Main Streamlit app
├── database/
│   ├── nf_buildathon.db   # SQLite database
│   └── schema.sql         # Reference schema
├── agent/
│   ├── sql_generator.py   # LLM → SQL logic
│   ├── validator.py       # Read-only enforcement
│   └── clarifier.py       # Ambiguity detection & follow-up
├── utils/
│   └── visualization.py   # Chart generation helpers
└── prompts/
    └── system_prompt.txt  # LLM system prompt with schema context
```

---

## 7. Success Metrics (How We Measure)

### For the Hackathon (Judging Criteria)
| Metric | Target |
|--------|--------|
| **Query accuracy** | Correct SQL on first attempt for 8/10 test questions |
| **Ambiguity handling** | Catches 3+ ambiguous queries and asks instead of guessing |
| **Safety** | Zero SQL injection / write operations allowed |
| **Response time** | Under 5 seconds per query |
| **UX** | Non-technical user can get 3 correct answers without help |

### For Product-Market Fit (Post-Hackathon)
| Metric | Target |
|--------|--------|
| **Weekly active users** | 10+ non-engineering team members using it |
| **Data team ticket reduction** | 40% fewer ad-hoc data requests |
| **Query success rate** | >85% first-try correct answers |
| **Time-to-answer** | From 4 hours → <30 seconds |
| **Net Promoter Score** | >40 from internal users |

---

## 8. What We Are Deliberately NOT Building (V1 Out-of-Scope)

| Feature | Reason to Exclude |
|---------|------------------|
| **INSERT/UPDATE/DELETE operations** | Safety first — V1 is read-only by design and enforcement |
| **User authentication / login** | Adds 0 value to the hackathon demo; single-user is sufficient |
| **Chat history persistence** | Requires a second database; not needed for a demo walkthrough |
| **Voice input** | Adds STT failure modes; validates poorly in a noisy hackathon floor |
| **Multi-language support beyond Hinglish** | Hinglish validates the concept; other languages are localization |
| **Dashboard / saved reports** | The value prop is ad-hoc Q&A, not dashboards (which already exist) |
| **Mobile app** | Streamlit is responsive but this is desktop-first for internal use |
| **Query optimization / indexing** | 40K records on SQLite doesn't need it |
| **Advanced visualizations** (maps, heatmaps) | Bar/line charts cover 90% of ad-hoc questions |
| **Feedback/rating system** | "Was this helpful?" is nice but not a judging criteria |
| **Multi-turn conversation memory** | Each query is independent; follow-ups re-inject context |
| **PDF/CSV export** | User can copy-paste from the table; export is V2 quality-of-life |
| **Role-based access control** | No auth means no roles; all queries are equal in V1 |
| **On-premise deployment** | Local demo or Streamlit Cloud is sufficient |

---

## 9. Edge Cases & Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| **Hallucinated table/column names** | Inject actual schema + 2-3 sample rows per table in system prompt |
| **Ambiguous question** | Classifier detects ambiguity → asks question back, never guesses |
| **Hinglish parsing fails** | System prompt includes common Hinglish patterns + few-shot examples |
| **Query times out (>10s)** | Set LLM timeout + SQLite query timeout; show "Taking longer than expected" |
| **SQL returns 1000+ rows** | Auto-limit to 50 rows with "Showing 50 of N results" note |
| **No results found** | Instead of empty table, say "No data matches your query. Try..." suggestions |
| **User asks non-database question** | Classifier detects out-of-domain → "I can only answer questions about NikahForever data. Try asking about users, matches, or payments." |

---

## 10. Suggested Build Order (Hackathon Timeline)

| Time | Task |
|------|------|
| **Hour 1** | Explore schema, test LLM API, set up Streamlit skeleton |
| **Hour 2** | Build SQL generator + validator + clarifier |
| **Hour 3** | Wire up UI — chat input, response display, SQL reveal |
| **Hour 4** | Add charting + Hinglish prompts + error handling |
| **Hour 5** | Polish — greetings, suggestion chips, error messages, demo script |
| **Hour 6** | Buffer for debugging + record demo video + submit |
