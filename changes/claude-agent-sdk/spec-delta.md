# Spec Delta: Claude Agent SDK

## ADDED

### 1. Research Agent

#### 1.1 Web Search & Data Gathering
```
Given a company name (e.g., "Stripe") is provided as pipeline input
When the Research Agent is invoked via the orchestrator
Then it searches the web for recent news, financials, and competitor data
And it pulls company filings (10-K, 10-Q or equivalent)
And it gathers competitor landscape data
And it outputs a structured JSON brief containing: company_overview, financials, competitors, recent_news
```

#### 1.2 Research Agent — No Results Found
```
Given a company name that yields no web search results (e.g., fictitious company)
When the Research Agent is invoked
Then it returns a brief with empty sections clearly marked as "no data found"
And it does NOT hallucinate data to fill gaps
And it logs a warning indicating insufficient source data
```

#### 1.3 Research Agent — MCP Tool Binding
```
Given the Research Agent is configured
When it is initialized via Claude Agent SDK
Then it connects to 3 MCP tool servers: web_search, calculator, file_writer
And each tool is callable via the MCP protocol
```

---

### 2. Analysis Agent

#### 2.1 Financial Analysis & Scoring
```
Given the Research Agent has produced a valid structured brief
When the orchestrator passes the brief to the Analysis Agent
Then it performs financial calculations (revenue growth, margins, ratios)
And it identifies key risks (market, regulatory, operational)
And it outputs an opportunity_score (1-10 scale) with justification
And the output is a structured JSON containing: calculations, risks, opportunity_score, justification
```

#### 2.2 Analysis Agent — Incomplete Brief
```
Given the Research Agent brief has missing financial data
When the Analysis Agent receives the incomplete brief via the orchestrator
Then it performs analysis on available data only
And it flags missing fields in its output as "insufficient data"
And it adjusts the opportunity_score confidence level accordingly
```

#### 2.3 Analysis Agent — MCP Tool Binding
```
Given the Analysis Agent is configured
When it is initialized via Claude Agent SDK
Then it connects to 3 MCP tool servers: web_search, calculator, file_writer
```

---

### 3. Writer Agent

#### 3.1 Investment Memo Drafting
```
Given the Analysis Agent has produced a valid analysis output
When the orchestrator passes the analysis to the Writer Agent
Then it drafts a 2-page investment memo in markdown format
And the memo follows the company template structure: Executive Summary, Company Overview, Financial Analysis, Risk Assessment, Recommendation
And the memo references specific data points from the analysis output
```

#### 3.2 Writer Agent — Output Validation
```
Given the Writer Agent has produced a memo
When the orchestrator validates the output
Then it checks the memo contains all required sections (Executive Summary, Company Overview, Financial Analysis, Risk Assessment, Recommendation)
And it checks the memo length is approximately 2 pages (800-1200 words)
And if validation fails, the orchestrator re-invokes the Writer Agent with revision instructions
And output validation retries up to a maximum of 3 attempts
And if still invalid after 3 attempts, the pipeline exits with a warning and the best-effort memo
```

#### 3.3 Writer Agent — Input Validation
```
Given the orchestrator receives analysis output for the Writer Agent
When the output is missing required fields (calculations, risks, opportunity_score)
Then the orchestrator rejects the input before invoking the Writer Agent
And an error is raised with a descriptive message listing missing fields
```

#### 3.4 Writer Agent — MCP Tool Binding
```
Given the Writer Agent is configured
When it is initialized via Claude Agent SDK
Then it connects to 3 MCP tool servers: web_search, calculator, file_writer
And the file_writer MCP server is used to save the memo to disk
```

---

### 4. QA/Review Agent

#### 4.1 Factual Consistency Check
```
Given the Writer Agent has produced a memo AND the orchestrator retains the original research brief
When the orchestrator passes both the memo and the research brief to the QA/Review Agent
Then it cross-references every factual claim in the memo against the research brief
And it produces a consistency_report with: verified_claims[], unverified_claims[], flagged_hallucinations[]
And each flagged item includes the memo excerpt and the expected source data
```

#### 4.2 Hallucination Detection
```
Given the memo contains a data point not present in the research brief
When the QA/Review Agent checks that claim
Then it flags it as a potential hallucination
And it includes a suggested correction or removal in the report
```

#### 4.3 Revision Request
```
Given the QA/Review Agent finds flagged_hallucinations.length > 0
When the consistency report is generated
Then it returns a revision_required: true flag
And it includes specific revision instructions for each flagged item
```

#### 4.4 Revision Loop
```
Given the QA/Review Agent returns revision_required: true
When the orchestrator receives the revision request
Then it re-invokes the Writer Agent with the revision instructions and original analysis
And the QA/Review Agent re-checks the revised memo
And this loop repeats up to a maximum of 3 revision cycles
And if still flagged after 3 cycles, the pipeline exits with a warning and the best-effort memo
```

#### 4.5 QA Agent — Clean Pass
```
Given the memo has zero hallucinations and all claims are verified
When the QA/Review Agent completes its review
Then it returns revision_required: false
And the pipeline completes successfully with the final memo
```

#### 4.6 QA Agent — MCP Tool Binding
```
Given the QA/Review Agent is configured
When it is initialized via Claude Agent SDK
Then it connects to 3 MCP tool servers: web_search, calculator, file_writer
```

---

### 5. Orchestrator Pipeline

#### 5.1 Sequential Execution — Happy Path
```
Given the orchestrator is initialized with all 4 agents configured
When a company name is provided as input
Then the orchestrator invokes agents sequentially: Research → Analysis → Writer → QA
And it passes the structured JSON output of each agent as input to the next
And it retains all intermediate outputs for cross-referencing (especially for QA)
And the pipeline completes with a final investment memo
```

#### 5.2 Orchestrator — State Accumulation
```
Given Agent 1 (Research) produces a JSON brief
When the orchestrator progresses through the pipeline
Then the orchestrator maintains a shared state object containing all prior agent outputs
And the QA Agent receives: { research_brief, analysis_output, memo } for full cross-referencing
```

#### 5.3 Orchestrator — Agent Failure Handling
```
Given an agent raises an exception during processing
When the orchestrator detects the failure
Then it logs the error with agent name, stage, and full stack trace
And it does NOT silently continue with missing data
And it aborts the pipeline with a descriptive error report
```

---

### 6. Agent Handoffs (Evaluation Dimension)

#### 6.1 Handoff — Structured Output Integrity
```
Given Agent 1 (Research) produces a JSON brief with all top-level fields (company_overview, financials, competitors, recent_news)
When the orchestrator passes it to Agent 2 (Analysis)
Then Agent 2 receives all top-level fields intact
And field types are preserved (strings, numbers, arrays)
```

#### 6.2 Handoff — Benchmark (20 runs)
```
Given the pipeline is configured for benchmark mode with a canonical test input
When the pipeline is executed 20 times with the same company name and configuration
Then the handoff success rate is recorded (target: >95%)
And each run's handoff status (success/failure) is logged
And a summary report is saved as both benchmark_report.json (structured, machine-readable) and benchmark_report.md (human-readable with tables)
```

---

### 7. Tool Integration via MCP (Evaluation Dimension)

#### 7.1 MCP Server Setup
```
Given each agent requires 3 tools: web_search, calculator, file_writer
When the MCP tool servers are started
Then each server exposes its tool via the MCP protocol
And total lines of code to configure all MCP servers is recorded
And each agent can invoke its tools through the MCP connection
```

#### 7.2 Tool Error Rate
```
Given MCP tool servers are running and the pipeline runs 20 times
When any MCP tool call fails (timeout, connection error, bad response)
Then the error is logged with tool name, agent name, and error type
And the error rate per tool is calculated and reported
```

#### 7.3 MCP Server — Connection Failure
```
Given an MCP tool server is unreachable at pipeline start
When an agent attempts to connect to the server
Then the agent logs the connection error with server name and address
And the pipeline aborts with a descriptive error before processing begins
```

---

### 8. Memory / State (Evaluation Dimension)

#### 8.1 End-to-End State Retention
```
Given Agent 1 (Research) discovers a specific data point (e.g., "revenue = $1.2B")
When Agent 4 (QA) reviews the final memo
Then Agent 4 can verify that data point against the original research via the orchestrator's shared state
And the factual consistency score measures how accurately state is preserved across all 4 agents
```

#### 8.2 State Loss Detection
```
Given a data point is present in Agent 1's output but absent from the final memo
When the QA Agent runs its consistency check
Then the missing data point is flagged as a state loss
And the factual consistency score is reduced accordingly
```

---

### 9. Error Recovery (Evaluation Dimension)

#### 9.1 MCP Tool Failure Mid-Run
```
Given the pipeline is running and an MCP tool server crashes mid-execution
When the agent attempts to use the failed tool
Then the agent retries the MCP tool call (up to 3 attempts)
Or the agent fails gracefully with a descriptive error message
And the recovery rate and time-to-recover are logged
```

#### 9.2 Agent Crash Recovery
```
Given an agent raises an unhandled exception during processing
When the orchestrator detects the failure
Then the orchestrator logs the error with full stack trace
And it does NOT silently continue with missing data
And it reports which agent failed and at what stage
```

---

### 10. Developer Experience (Evaluation Dimension)

#### 10.1 DX Measurement
```
Given a developer starts from an empty claude-agent-sdk/ directory
When they build the full 4-agent pipeline to first working run
Then the total build time (hours) is recorded
And notable friction points are documented (MCP setup, handoff wiring, debugging)
And the result is stored for cross-SDK comparison
```

---

### 11. Observability (Evaluation Dimension)

#### 11.1 Structured Logging
```
Given the pipeline uses structured logging (Python logging or equivalent)
When a full pipeline run completes
Then a log is generated covering all 4 agent invocations
And each log entry includes: agent_name, start_time, end_time, tokens_used, tool_calls
And logs can be exported or printed for review
```

#### 11.2 Error Tracing
```
Given an error occurs at any point in the pipeline
When the logs are reviewed
Then the failing agent and exact step are identifiable
And the log includes the error message and context
```

---

### 12. Token Efficiency (Evaluation Dimension)

#### 12.1 Token Tracking
```
Given the pipeline completes a full run
When token usage is aggregated
Then total tokens (prompt + completion) are recorded per agent
And total cost per run is calculated based on Anthropic model pricing
And the results are stored for cross-SDK comparison
```

#### 12.2 Token Reporting
```
Given multiple runs have been completed
When the benchmark report is generated
Then it includes: avg_tokens_per_run, avg_cost_per_run, tokens_per_agent breakdown
And the report is saved as both benchmark_report.json and benchmark_report.md for cross-SDK comparison
```

---

### 13. Configuration & Validation

#### 13.1 API Key Validation
```
Given the ANTHROPIC_API_KEY environment variable is not set or is invalid
When the pipeline starts
Then it exits immediately with a clear error message: "ANTHROPIC_API_KEY is missing or invalid"
And no API calls are made
```

#### 13.2 Canonical Test Input
```
Given the pipeline is run in benchmark mode
When the canonical test input is used
Then the company name is "Stripe" (or a configured default)
And the configuration is identical across all 20 runs for reproducibility
```

---

### 14. Project Structure

#### 14.1 Directory Layout
```
Given the implementation is created
When a developer inspects the project
Then the following structure exists:
  claude-agent-sdk/
  ├── agents/
  │   ├── research_agent.py
  │   ├── analysis_agent.py
  │   ├── writer_agent.py
  │   └── qa_agent.py
  ├── tools/
  │   ├── web_search_server.py    # MCP server
  │   ├── calculator_server.py    # MCP server
  │   └── file_writer_server.py   # MCP server
  ├── pipeline.py                 # orchestrator — sequential agent execution
  ├── benchmark.py                # runs 20-run evaluation
  ├── config.py                   # API keys, model settings
  └── requirements.txt
```

---

## MODIFIED
- None (first implementation — no existing specs to modify)

## REMOVED
- None
