Multi-Agent SDK Comparison
Test OpenAI Agents SDK, Google ADK, and Claude Agent SDK by building the same multi-agent pipeline in each framework and comparing results across 7 key dimensions

## **Agent Roles**

- **Research Agent** — Searches the web, pulls company filings, gathers competitor data into a structured brief
- **Analysis Agent** — Takes the brief, runs financial calculations, identifies risks, scores the opportunity
- **Writer Agent** — Drafts a 2-page investment memo using analysis output, following a company template
- **QA/Review Agent** — Checks the memo for factual consistency against research data, flags hallucinations, requests revisions

## **Evaluation Dimensions**

| Dimension | What to Test | How to Measure |
|-----------|--------------|----------------|
| Agent Handoffs | Can Agent 1 cleanly pass structured output to Agent 2? | Success rate across 20 runs |
| Tool Integration | Connect each agent to 3 tools (web search, calculator, file writer) | Lines of code to configure, error rate |
| Memory / State | Does Agent 4 accurately recall what Agent 1 found? | Factual consistency score |
| Error Recovery | Kill a tool mid-run — does the agent retry or fail gracefully? | Recovery rate, time to recover |
| Developer Experience | Time to build, debug, and deploy the full pipeline | Hours to first working prototype |
| Observability | Can you trace a full run and identify where things went wrong? | Quality of built-in tracing/logs |
| Token Efficiency | Total tokens consumed for the same task | Cost per complete run |


SDK-Specific Implementation Notes
OpenAI Agents SDK: Leverage native Agent.handoff_to pattern. Use built-in guardrails for input/output validation on the Writer Agent. Tracing is built-in via the SDK's trace logger.
Google ADK: Use hierarchical agent architecture with a root Orchestrator delegating to sub-agents. Test the built-in evaluation CLI (adk eval). Deploy to Cloud Run as a microservice for the production test.
Claude Agent SDK: Use MCP servers for tool connectivity. Test extended thinking mode on the Analysis Agent for transparent reasoning. Multi-agent handoffs must be built manually since the SDK focuses on single-agent depth.
