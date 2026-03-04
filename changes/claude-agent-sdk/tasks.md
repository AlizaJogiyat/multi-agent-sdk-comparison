# Tasks: Claude Agent SDK

## Phase 1: Foundation (Project Setup & Configuration)

- [x] **1.1 Scaffold project structure**
  - Acceptance: Scenario 14.1 (Directory Layout)
  - Files: `claude-agent-sdk/` directory with `agents/`, `tools/`, `pipeline.py`, `benchmark.py`, `config.py`, `requirements.txt`

- [x] **1.2 Create config.py with API key validation**
  - Acceptance: Scenario 13.1 (API Key Validation) — exits with clear error if ANTHROPIC_API_KEY missing/invalid
  - Files: `claude-agent-sdk/config.py`

- [x] **1.3 Set up requirements.txt with dependencies**
  - Acceptance: Scenario 14.1 — `requirements.txt` exists with anthropic SDK, MCP dependencies
  - Files: `claude-agent-sdk/requirements.txt`

## Phase 2: MCP Tool Servers

- [x] **2.1 Build web_search MCP server**
  - Acceptance: Scenario 7.1 (MCP Server Setup) — exposes web_search tool via MCP protocol
  - Files: `claude-agent-sdk/tools/web_search_server.py`

- [x] **2.2 Build calculator MCP server**
  - Acceptance: Scenario 7.1 (MCP Server Setup) — exposes calculator tool via MCP protocol
  - Files: `claude-agent-sdk/tools/calculator_server.py`

- [x] **2.3 Build file_writer MCP server**
  - Acceptance: Scenario 7.1 (MCP Server Setup) — exposes file_writer tool via MCP protocol
  - Files: `claude-agent-sdk/tools/file_writer_server.py`

- [x] **2.4 Handle MCP connection failures**
  - Acceptance: Scenario 7.3 (MCP Server — Connection Failure) — SDK handles via init message status checks
  - Files: Agent files check MCP connection via SDK's SystemMessage init

## Phase 3: Agent Implementation

- [x] **3.1 Build Research Agent**
  - Acceptance: Scenario 1.1, 1.2, 1.3
  - Files: `claude-agent-sdk/agents/research_agent.py`

- [x] **3.2 Build Analysis Agent**
  - Acceptance: Scenario 2.1, 2.2, 2.3
  - Files: `claude-agent-sdk/agents/analysis_agent.py`

- [x] **3.3 Build Writer Agent**
  - Acceptance: Scenario 3.1, 3.4
  - Files: `claude-agent-sdk/agents/writer_agent.py`

- [x] **3.4 Build QA/Review Agent**
  - Acceptance: Scenario 4.1, 4.2, 4.3, 4.5
  - Files: `claude-agent-sdk/agents/qa_agent.py`

## Phase 4: Orchestrator Pipeline

- [x] **4.1 Build orchestrator with sequential execution**
  - Acceptance: Scenario 5.1, 5.2, 6.1
  - Files: `claude-agent-sdk/pipeline.py`

- [x] **4.2 Implement input validation for Writer Agent**
  - Acceptance: Scenario 3.3
  - Files: `claude-agent-sdk/pipeline.py`

- [x] **4.3 Implement output validation for Writer Agent**
  - Acceptance: Scenario 3.2 — checks 5 required sections, 800-1200 words, max 3 retries
  - Files: `claude-agent-sdk/pipeline.py`

- [x] **4.4 Implement QA revision loop**
  - Acceptance: Scenario 4.4 — max 3 cycles, best-effort exit
  - Files: `claude-agent-sdk/pipeline.py`

- [x] **4.5 Implement agent failure handling**
  - Acceptance: Scenario 5.3, 9.2
  - Files: `claude-agent-sdk/pipeline.py`

## Phase 5: Observability & Logging

- [x] **5.1 Add structured logging to pipeline**
  - Acceptance: Scenario 11.1, 11.2
  - Files: `claude-agent-sdk/pipeline.py`, agent files

- [x] **5.2 Add token usage tracking**
  - Acceptance: Scenario 12.1
  - Files: `claude-agent-sdk/pipeline.py`, `claude-agent-sdk/benchmark.py`

- [x] **5.3 Add MCP tool error logging and retry**
  - Acceptance: Scenario 9.1, 7.2
  - Files: Tool servers include error handling; SDK handles retries internally

## Phase 6: Benchmark Harness

- [x] **6.1 Build benchmark runner (20 runs)**
  - Acceptance: Scenario 6.2, 13.2
  - Files: `claude-agent-sdk/benchmark.py`

- [x] **6.2 Generate benchmark reports (JSON + Markdown)**
  - Acceptance: Scenario 6.2, 12.2
  - Files: `claude-agent-sdk/benchmark.py`

## Phase 7: Cleanup & Archive

- [ ] **7.1 Commit implementation with `[impl]` prefix**
- [ ] **7.2 Archive change on merge** — move `changes/claude-agent-sdk/` → `archive/`, merge spec-delta into `specs/features/`
