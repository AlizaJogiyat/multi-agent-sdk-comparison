export interface SDK {
  name: string;
  slug: string;
  tagline: string;
  status: "active" | "placeholder";
  color: string;
  icon: string;
  description: string;
  features: string[];
  architecture: string;
  agents: { name: string; role: string }[];
}

export const sdks: Record<string, SDK> = {
  claude: {
    name: "Claude Agent SDK",
    slug: "claude",
    tagline: "Multi-agent pipeline with tool use and streaming",
    status: "active",
    color: "#D97706",
    icon: "🟠",
    description:
      "Built with the Anthropic Python SDK, this pipeline uses Claude's native tool-use capability to orchestrate 3 agents in sequence. Each agent has its own system prompt, tool definitions, and an agentic loop that runs until the model signals completion.",
    features: [
      "Native tool_use with structured input schemas",
      "Agentic loop — iterates until stop_reason is end_turn",
      "Sequential handoff — Agent 1 output feeds Agent 2, both feed Agent 3",
      "Real Wikipedia data fetching via tool execution",
      "Structured memo formatting via format_memo tool",
    ],
    architecture:
      "Researcher Agent → Analyzer Agent → Writer Agent → QA/Review Agent. The orchestrator passes each agent's text output as context to the next. All agents share a common tool dispatcher.",
    agents: [
      { name: "Researcher", role: "Fetches company data from Wikipedia" },
      { name: "Analyzer", role: "Calculates metrics and scores the opportunity" },
      { name: "Writer", role: "Drafts a 2-page investment memo from research + analysis" },
      { name: "QA/Review", role: "Fact-checks memo against research, flags hallucinations" },
    ],
  },
  openai: {
    name: "OpenAI Agents SDK",
    slug: "openai",
    tagline: "Agent orchestration with built-in handoffs and guardrails",
    status: "placeholder",
    color: "#10A37F",
    icon: "🟢",
    description:
      "The OpenAI Agents SDK provides primitives for building agentic systems: Agents with instructions and tools, automatic handoffs between agents, guardrails for input/output validation, and built-in tracing for observability.",
    features: [
      "Declarative agent definitions with instructions + tools",
      "Built-in handoff mechanism between agents",
      "Input/output guardrails",
      "Native tracing and observability",
      "Runner.run() orchestration loop",
    ],
    architecture:
      "Same 3-agent pipeline (Researcher → Analyzer → Writer) will be implemented using the OpenAI Agents SDK's Runner and handoff primitives.",
    agents: [
      { name: "Researcher", role: "Fetches company data" },
      { name: "Analyzer", role: "Scores the investment opportunity" },
      { name: "Writer", role: "Drafts the investment memo" },
    ],
  },
  "google-adk": {
    name: "Google ADK",
    slug: "google-adk",
    tagline: "Agent Development Kit with Gemini-powered orchestration",
    status: "placeholder",
    color: "#4285F4",
    icon: "🔵",
    description:
      "Google's Agent Development Kit (ADK) provides a framework for building multi-agent systems powered by Gemini models. It supports tool use, agent-to-agent communication, and integration with Google Cloud services.",
    features: [
      "Gemini model integration",
      "Multi-agent orchestration",
      "Google Cloud tool ecosystem",
      "Built-in session and memory management",
      "Agent-to-agent delegation",
    ],
    architecture:
      "Same 3-agent pipeline (Researcher → Analyzer → Writer) will be implemented using Google ADK's agent framework and Gemini models.",
    agents: [
      { name: "Researcher", role: "Fetches company data" },
      { name: "Analyzer", role: "Scores the investment opportunity" },
      { name: "Writer", role: "Drafts the investment memo" },
    ],
  },
};

export const sdkList = Object.values(sdks);
