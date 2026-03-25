# Claude Agent SDK — What We Built & How

## Overview

We built a **4-agent investment memo pipeline** using the Claude Agent SDK (Anthropic Python SDK) as part of a multi-SDK benchmarking project. The pipeline takes a company name as input and produces a complete investment memo through sequential agent collaboration.

---

## The Pipeline

```
User Input (Company Name)
        │
        ▼
┌─────────────────┐
│  1. Researcher   │  → Fetches real company data from Wikipedia
└────────┬────────┘
         │ structured research brief
         ▼
┌─────────────────┐
│  2. Analyzer     │  → Scores opportunity, calculates financial metrics
└────────┬────────┘
         │ analysis + scores
         ▼
┌─────────────────┐
│  3. Writer       │  → Drafts a 2-page investment memo
└────────┬────────┘
         │ formatted memo
         ▼
┌─────────────────┐
│  4. QA / Review  │  → Fact-checks, flags hallucinations & inconsistencies
└─────────────────┘
         │
         ▼
   Final Output (Research + Analysis + Memo + QA Review)
```

---

## How Each Agent Works

### Agent 1: Researcher
- **Tool:** `search_company_info`
- Calls the Wikipedia API to fetch real company data (founding year, sector, headquarters, summary).
- Returns a structured research brief for downstream agents.

### Agent 2: Analyzer
- **Tools:** `calculate_metric`, `score_opportunity`
- Receives the Researcher's output as context.
- Computes financial metrics and assigns an investment score with rationale.

### Agent 3: Writer
- **Tool:** `format_memo`
- Receives outputs from both the Researcher and Analyzer.
- Produces a structured memo with sections: Executive Summary, Company Overview, Financial Analysis, Investment Thesis, Risks, and Recommendation.

### Agent 4: QA / Review
- **Tools:** `fact_check`, `flag_issue`
- Cross-references the memo against the original research.
- Flags hallucinations, unsupported claims, and inconsistencies with severity levels.
- Suggests revisions where needed.

---

## Core Technical Pattern: The Agentic Loop

Each agent follows the same loop pattern using the raw Anthropic SDK (`anthropic` Python package):

```python
# 1. Call Claude with tools
response = client.messages.create(
    model="claude-sonnet-4-6",
    messages=messages,
    tools=agent_tools,
    max_tokens=4096
)

# 2. Loop while the model wants to use tools
while response.stop_reason == "tool_use":
    # Extract tool call, execute it, append result to messages
    tool_result = process_tool_call(response)
    messages.append(assistant_response)
    messages.append(tool_result)
    response = client.messages.create(...)  # re-call with updated messages

# 3. Exit when stop_reason == "end_turn"
```

There is no external orchestration framework — we built the agent loop, tool dispatch, and handoff logic ourselves using the Anthropic SDK's native `tool_use` capability.

---

## Handoff Mechanism

Agents pass data **sequentially via structured output**. Each agent's final text output is injected into the next agent's system/user prompt as context. There is no shared memory store — it's a simple, explicit chain.

---

## Web Application

We wrapped the pipeline in a full-stack web app for interactive testing:

### Backend — FastAPI
- `POST /api/run/claude` streams results via **Server-Sent Events (SSE)**.
- An async runner (`claude_runner.py`) wraps the synchronous agent loop and emits real-time events: `pipeline_start`, `agent_start`, `tool_call`, `tool_result`, `agent_complete`, `pipeline_complete`.

### Frontend — Next.js 15 + React 19 + Tailwind CSS
- Home page shows SDK cards (Claude is "Live", OpenAI and Google ADK are "Coming Soon").
- SDK detail page (`/sdk/claude`) has an interactive **TestNowForm**.
- Live **terminal-style output** with color-coded events (yellow for agent start, purple for tool calls, green for completion).
- **Download Report** button generates a PDF with all 4 agent outputs using jsPDF.

---

## Project Structure

```
multi-agent-sdk-comparison/
├── claude-agent/
│   └── agent_system.py        # Core 4-agent pipeline (865 lines)
├── api/
│   ├── main.py                # FastAPI app with CORS
│   ├── routers/run.py         # Endpoint for each SDK
│   └── services/
│       └── claude_runner.py   # Async SSE streaming wrapper
├── frontend/
│   ├── app/                   # Next.js App Router pages
│   ├── components/            # SdkCard, TestNowForm, TerminalOutput
│   └── lib/sdk-data.ts        # SDK metadata
└── README.md
```

---

## Key Dependencies

| Layer    | Tech                                                     |
| -------- | -------------------------------------------------------- |
| AI Model | `claude-sonnet-4-6` via `anthropic` Python SDK            |
| Backend  | FastAPI, Uvicorn, sse-starlette                          |
| Frontend | Next.js 15, React 19, Tailwind CSS 4, TypeScript, jsPDF |
| Data     | Wikipedia API, BeautifulSoup4                            |

---

## How to Run

```bash
# Backend
cd api
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev    # → http://localhost:3000

# CLI only (no web app)
cd claude-agent
python agent_system.py
```

---

## What We Learned

- The Anthropic SDK's `tool_use` stop reason makes building agentic loops straightforward — no framework needed.
- Sequential handoffs via prompt injection are simple and effective for linear pipelines.
- SSE streaming gives a great real-time UX for long-running multi-agent workflows.
- The QA agent catching hallucinations from earlier agents demonstrates genuine multi-agent value.
