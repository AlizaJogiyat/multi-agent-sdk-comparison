# Constitution: Multi-Agent SDK Comparison

## Immutable Principles

1. **Spec Before Code** — No behavior-changing code is written without a committed specification.
2. **Fair Comparison** — All three SDK implementations (OpenAI Agents SDK, Google ADK, Claude Agent SDK) MUST implement the same spec so results are directly comparable.
3. **Same Pipeline** — The pipeline is always: Research Agent → Analysis Agent → Writer Agent → QA/Review Agent.
4. **Structured Handoffs** — Agent outputs MUST be structured (JSON/typed objects) so handoff fidelity can be measured objectively.
5. **Evaluation Integrity** — All 7 evaluation dimensions (Handoffs, Tool Integration, Memory/State, Error Recovery, DX, Observability, Token Efficiency) are measured using the same methodology across all SDKs.
6. **Reproducibility** — Every benchmark run MUST be reproducible given the same inputs and configuration.
7. **Specs Are Source of Truth** — If code and spec disagree, the spec wins and the code is a bug.
