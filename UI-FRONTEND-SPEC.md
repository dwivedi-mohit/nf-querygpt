# Frontend Specification Document: NF QueryGPT

**Version:** 1.0
**Role:** Senior UI/UX Designer & Frontend Architect
**Date:** June 13, 2026
**Project:** Build With TRAE Hackathon — Track 4

---

## 1. Design System

### 1.1 Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| **Primary** | `#8B5CF6` | Brand color — buttons, links, active states, header |
| **Primary Hover** | `#7C3AED` | Button hover, interactive hover states |
| **Primary Light** | `#EDE9FE` | Background tints, selected chat bubbles, alert backgrounds |
| **Secondary** | `#F59E0B` | Accent — badges, highlights, warnings |
| **Success** | `#10B981` | Positive metrics, success states, verified badges |
| **Error** | `#EF4444` | Errors, failed payments, danger states |
| **Warning** | `#F59E0B` | Warnings, ambiguous query indicators |
| **Background** | `#FAFAFA` | Page background |
| **Surface** | `#FFFFFF` | Cards, chat bubbles, modals |
| **Surface Hover** | `#F3F4F6` | Card hover, row hover |
| **Text Primary** | `#111827` | Headings, body text |
| **Text Secondary** | `#6B7280` | Labels, descriptions, timestamps |
| **Text Muted** | `#9CA3AF` | Placeholders, disabled text |
| **Border** | `#E5E7EB` | Card borders, dividers, input borders |
| **Code Block** | `#1F2937` | SQL code block background |
| **Code Text** | `#E5E7EB` | SQL code block text |

### 1.2 Typography

| Token | Font | Size | Weight | Line Height | Usage |
|-------|------|------|--------|-------------|-------|
| **Display** | Inter | 28px | 700 | 1.2 | App title, welcome header |
| **Heading 1** | Inter | 22px | 600 | 1.3 | Section titles, query result count |
| **Heading 2** | Inter | 18px | 600 | 1.4 | Card titles, modal headers |
| **Body** | Inter | 14px | 400 | 1.5 | Chat messages, table content, descriptions |
| **Body Small** | Inter | 12px | 400 | 1.5 | Timestamps, footnotes, metadata |
| **Code** | JetBrains Mono | 13px | 400 | 1.6 | SQL display, error details |
| **Button** | Inter | 14px | 500 | 1 | Button labels |
| **Label** | Inter | 12px | 600 | 1 | Form labels, badge text |
| **Suggestion Chip** | Inter | 13px | 400 | 1 | Clickable suggestion chips |

**Font stack:** `Inter` for UI, `JetBrains Mono` for code blocks.

### 1.3 Component Styles

#### Buttons

| State | Primary | Secondary | Ghost | Danger |
|-------|---------|-----------|-------|--------|
| **Default** | `bg=#8B5CF6 text=white` | `bg=white border=#E5E7EB text=#111827` | `bg=transparent text=#8B5CF6` | `bg=white border=#EF4444 text=#EF4444` |
| **Hover** | `bg=#7C3AED` | `bg=#F9FAFB` | `bg=#EDE9FE` | `bg=#FEF2F2` |
| **Disabled** | `bg=#D4D4D8 text=#A1A1AA` | `bg=#F4F4F5 text=#A1A1AA` | `text=#A1A1AA` | `text=#A1A1AA` |
| **Radius** | 8px | 8px | 8px | 8px |
| **Padding** | 10px 20px | 10px 20px | 8px 16px | 10px 20px |

#### Input Fields (Chat Input)

| State | Style |
|-------|-------|
| **Default** | `bg=white border=#E5E7EB border-radius=12px padding=12px 16px` |
| **Focus** | `border=#8B5CF6 ring=2px ring-color=#8B5CF6/20` |
| **Disabled** | `bg=#F9FAFB text=#9CA3AF` |
| **Placeholder** | `text=#9CA3AF` "Ask me anything about NikahForever data..." |
| **Icon** | Send button: Primary filled circle with arrow icon |

#### Cards

| Token | Value |
|-------|-------|
| **Background** | `#FFFFFF` |
| **Border** | `1px solid #E5E7EB` |
| **Border Radius** | 12px |
| **Shadow** | `0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)` |
| **Padding** | 20px |
| **Hover Shadow** | `0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.04)` |

#### Chat Bubbles

| Token | User Message | AI Message |
|-------|-------------|------------|
| **Background** | `#8B5CF6` | `#F3F4F6` |
| **Text** | `#FFFFFF` | `#111827` |
| **Border Radius** | 16px 16px 4px 16px | 16px 16px 16px 4px |
| **Max Width** | 75% | 85% |
| **Padding** | 12px 16px | 12px 16px |
| **Margin Bottom** | 8px | 8px |

#### SQL Code Block (Collapsible)

| Token | Value |
|-------|-------|
| **Background** | `#1F2937` |
| **Text** | `#E5E7EB` |
| **Border Radius** | 8px |
| **Padding** | 16px |
| **Font** | JetBrains Mono 13px |
| **Toggle** | Chevron icon + "Show SQL" / "Hide SQL" label |
| **Copy Button** | Ghost icon button in top-right corner |

#### Tables

| Token | Value |
|-------|-------|
| **Header Background** | `#F9FAFB` |
| **Header Text** | `#6B7280` (uppercase, 11px, 600 weight) |
| **Row Hover** | `#F9FAFB` |
| **Border** | `1px solid #E5E7EB` |
| **Border Radius** | 8px |
| **Cell Padding** | 12px 16px |

#### Charts

| Token | Value |
|-------|-------|
| **Primary Series** | `#8B5CF6` |
| **Secondary Series** | `#F59E0B` |
| **Tertiary Series** | `#10B981` |
| **Grid Lines** | `#F3F4F6` |
| **Background** | Transparent |
| **Font** | Inter 12px |

#### Modals / Dialogs

| Token | Value |
|-------|-------|
| **Overlay** | `rgba(0,0,0,0.4)` |
| **Content Background** | `#FFFFFF` |
| **Border Radius** | 16px |
| **Padding** | 24px |
| **Shadow** | `0 20px 60px rgba(0,0,0,0.15)` |
| **Max Width** | 480px |

#### Suggestion Chips

| State | Style |
|-------|-------|
| **Default** | `bg=#EDE9FE text=#8B5CF6 border-radius=20px padding=6px 14px font-size=13px` |
| **Hover** | `bg=#8B5CF6 text=white cursor=pointer` |
| **Container** | Horizontal scroll, 8px gap between chips |

#### Loading States

| Element | Style |
|---------|-------|
| **Query Loading** | Pulsing purple dot animation + "Thinking..." text |
| **SQL Generating** | Typing indicator (three bouncing dots) |
| **Error State** | Red alert icon + error message in `#FEF2F2` background card |

### 1.4 Spacing & Layout

#### Spacing Scale

| Token | Pixels | Usage |
|-------|--------|-------|
| `space-1` | 4px | Tight inner padding, icon gaps |
| `space-2` | 8px | Component gaps, chip spacing |
| `space-3` | 12px | Input padding, button padding |
| `space-4` | 16px | Card padding, section spacing |
| `space-5` | 20px | Card padding (generous) |
| `space-6` | 24px | Modal padding, section separation |
| `space-8` | 32px | Page section gaps |
| `space-10` | 40px | Major layout breaks |
| `space-12` | 48px | Page margins |

#### Layout Rules

| Element | Rule |
|---------|------|
| **Page Max Width** | 960px centered |
| **Chat Container** | 100% width, max 720px |
| **Side Margins** | 24px mobile, 48px desktop |
| **Header Height** | 64px (sticky) |
| **Input Bar** | Fixed to bottom, 80px height |
| **Chat Area** | Scrollable, fills space between header and input |
| **Table Container** | Horizontally scrollable on overflow |
| **SQL Block** | Full width within card, horizontally scrollable |
| **Chart Container** | 100% width, aspect ratio 16:9 or auto |

---

## 2. API & Integration Specification

### 2.1 Service Inventory

| Service | Purpose | Type | Auth Method | Cost | Fallback |
|---------|---------|------|-------------|------|----------|
| **Groq** | Primary LLM for SQL generation | HTTP API | API Key (header) | Free (30 req/min) | OpenRouter |
| **OpenRouter** | Fallback LLM | HTTP API | API Key (header) | $0.15/M tokens | None |
| **SQLite** | Database (local file) | Local | None (file-based) | Free | N/A |

### 2.2 Groq API

#### Endpoint

```
POST https://api.groq.com/openai/v1/chat/completions
```

#### Headers

```
Authorization: Bearer gsk_xxxxxxxxxxxx
Content-Type: application/json
```

#### Request Body

```json
{
  "model": "llama-3.3-70b-versatile",
  "messages": [
    {
      "role": "system",
      "content": "You are a SQL generator for NikahForever matrimonial platform..."
    },
    {
      "role": "user",
      "content": "How many women signed up from Lucknow this month?"
    }
  ],
  "temperature": 0.1,
  "max_tokens": 1024
}
```

#### Response (Success)

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1718294400,
  "model": "llama-3.3-70b-versatile",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "{\"sql\": \"SELECT COUNT(*) FROM users WHERE gender = 'Female' AND city = 'Lucknow' AND created_at >= DATE('now', 'start of month')\", \"explanation\": \"This counts female users from Lucknow who registered this month.\", \"confidence\": 9}"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 850,
    "completion_tokens": 45,
    "total_tokens": 895
  }
}
```

#### Parsed Response Schema

```json
{
  "sql": "SELECT ...",
  "explanation": "Plain English explanation of what the query does",
  "confidence": 9
}
```

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `sql` | string | — | The generated SQL query (SELECT only) |
| `explanation` | string | — | Human-readable summary |
| `confidence` | integer | 1-10 | Confidence in matching user intent |

#### Response (Error)

```json
{
  "error": {
    "message": "Rate limit exceeded: 30 requests per minute",
    "type": "rate_limit_error",
    "code": 429
  }
}
```

### 2.3 OpenRouter API (Fallback)

#### Endpoint

```
POST https://openrouter.ai/api/v1/chat/completions
```

#### Headers

```
Authorization: Bearer sk-or-v1-xxxxxxxxxxxx
Content-Type: application/json
HTTP-Referer: https://nf-querygpt.demo
X-Title: NF QueryGPT
```

#### Request Body

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "system",
      "content": "You are a SQL generator for NikahForever matrimonial platform..."
    },
    {
      "role": "user",
      "content": "How many women signed up from Lucknow this month?"
    }
  ],
  "temperature": 0.1,
  "max_tokens": 1024
}
```

#### Response

Same structure as Groq (OpenAI-compatible format).

### 2.4 SQLite Database (Local)

#### Connection

```python
import sqlite3
conn = sqlite3.connect("database/nf_buildathon.db")
cursor = conn.cursor()
```

#### Execution Pattern

```python
def execute_safe_query(sql: str) -> dict:
    cursor.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchmany(MAX_ROWS_RETURNED + 1)
    truncated = len(rows) > MAX_ROWS_RETURNED
    return {
        "columns": columns,
        "rows": rows[:MAX_ROWS_RETURNED],
        "row_count": len(rows),
        "truncated": truncated
    }
```

### 2.5 Integration Data Flow

```
User Types Question
        │
        ▼
┌──────────────────────┐
│  Streamlit Frontend  │
│  (app.py)            │
│  Question + Context  │
└─────────┬────────────┘
          │  local function call
          ▼
┌──────────────────────┐
│  orchestrator.py     │
│                      │
│  1. Build prompt     │
│  2. Call LLM →       │───────► Groq API (or OpenRouter)
│  3. Parse response   │◄─────── {sql, explanation, confidence}
│  4. Validate SQL     │
│  5. Execute SQL →    │───────► SQLite (local file)
│  6. Format results   │◄─────── {columns, rows, row_count}
│  7. Return to UI     │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│  Streamlit Frontend  │
│                      │
│  Display:            │
│  • Explanation text  │
│  • Table / Chart     │
│  • SQL (collapsible) │
│  • Error if any      │
└──────────────────────┘
```

### 2.6 Loading & Error States

| State | Component | What User Sees |
|-------|-----------|----------------|
| **Loading** | Chat message | AI avatar + pulsing dots + "Generating SQL..." |
| **Executing** | Chat message | AI avatar + spinner + "Running query..." |
| **Success** | Chat message | AI response with results |
| **Error: LLM Down** | Chat message | Red alert: "AI service busy. Wait 30s." |
| **Error: Invalid SQL** | Chat message | Yellow alert: "Retrying with correction..." |
| **Error: Timeout** | Chat message | Orange alert: "Query too slow. Try narrowing." |
| **Error: Blocked** | Chat message | Red alert: "Query blocked (write attempt detected)" |
| **Error: No Results** | Chat message | Info card: "No data found" + suggestion chips |
| **Empty Input** | Input bar | Submit button disabled |

### 2.7 Rate Limiting & Circuit Breaker

```python
MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 2
RATE_LIMIT_WINDOW = 60
MAX_REQUESTS_PER_WINDOW = 25

# 1st failure → wait 2s → retry
# 2nd failure → switch to OpenRouter fallback
# OpenRouter failure → show user-friendly error
```

### 2.8 Configuration (`.env`)

```bash
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MAX_TOKENS=1024
GROQ_TEMPERATURE=0.1

OPENROUTER_API_KEY=sk-or-v1-your_key_here
OPENROUTER_MODEL=gpt-4o-mini
OPENROUTER_FALLBACK_ENABLED=true

DB_PATH=database/nf_buildathon.db
MAX_ROWS_RETURNED=100
QUERY_TIMEOUT_SECONDS=10
AMBIGUITY_THRESHOLD=7

APP_TITLE=NF QueryGPT
APP_DESCRIPTION="Ask anything about NikahForever data in plain English or Hinglish"
```
