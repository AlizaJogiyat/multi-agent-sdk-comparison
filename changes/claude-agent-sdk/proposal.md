# Proposal: Claude Agent SDK

## Problem
No implementation exists yet for the investment memo pipeline. We need to build the first SDK implementation (Claude Agent SDK) to establish a baseline for comparison against OpenAI Agents SDK and Google ADK.

## Solution
Build the complete 4-agent investment memo pipeline using Claude Agent SDK:
1. **Research Agent** — Searches the web, pulls company filings, gathers competitor data into a structured brief
2. **Analysis Agent** — Takes the brief, runs financial calculations, identifies risks, scores the opportunity
3. **Writer Agent** — Drafts a 2-page investment memo using analysis output, following a company template
4. **QA/Review Agent** — Checks the memo for factual consistency against research data, flags hallucinations, requests revisions

Leverage SDK-specific features:
- **MCP servers** for tool connectivity (web search, calculator, file writer)
- **Orchestrator pattern** for multi-agent handoffs (central pipeline calls each agent sequentially, passing structured output forward)
- Standard mode for all agents (no extended thinking)

Evaluate across all 7 dimensions: Handoffs, Tool Integration, Memory/State, Error Recovery, DX, Observability, Token Efficiency.

## Scope
- New `claude-agent-sdk/` directory with full pipeline implementation
- 3 MCP tool servers: web search, calculator, file writer
- Orchestrator pipeline that manages sequential agent execution and data passing
- Benchmark harness for 20-run handoff success rate
- Token usage tracking for cost-per-run measurement
- Logging setup for observability evaluation

## Risks
- API key management and secure credential handling
- Anthropic API rate limits during 20-run benchmarks
- Token cost accumulation during repeated benchmark runs
- Manual handoff implementation complexity (SDK focuses on single-agent depth)
- MCP server setup overhead compared to simple function-calling
