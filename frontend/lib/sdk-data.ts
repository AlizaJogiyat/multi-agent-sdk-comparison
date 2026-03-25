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
    tagline: "Agent orchestration with Runner.run() and @function_tool",
    status: "active",
    color: "#10A37F",
    icon: "🟢",
    description:
      "Built with the OpenAI Agents SDK, this pipeline uses declarative Agent definitions with @function_tool decorators and Runner.run() to orchestrate 4 agents in sequence. Each agent has its own instructions, tools, and the SDK handles the agentic loop automatically.",
    features: [
      "Declarative Agent() definitions with instructions + tools",
      "@function_tool decorator for tool definitions",
      "Runner.run() handles the agentic loop automatically",
      "Sequential handoff — each agent's output feeds the next",
      "Real Wikipedia data fetching via tool execution",
      "Structured memo formatting via format_memo tool",
    ],
    architecture:
      "Researcher Agent → Analyzer Agent → Writer Agent → QA/Review Agent. The orchestrator passes each agent's final_output as context to the next. Runner.run() manages tool calling loops internally.",
    agents: [
      { name: "Researcher", role: "Fetches company data from Wikipedia" },
      { name: "Analyzer", role: "Calculates metrics and scores the opportunity" },
      { name: "Writer", role: "Drafts a 2-page investment memo from research + analysis" },
      { name: "QA/Review", role: "Fact-checks memo against research, flags hallucinations" },
    ],
  },
  "google-adk": {
    name: "Google ADK",
    slug: "google-adk",
    tagline: "Agent Development Kit with Gemini-powered orchestration",
    status: "active",
    color: "#4285F4",
    icon: "🔵",
    description:
      "Built with Google's Agent Development Kit (ADK), this pipeline uses Gemini models with ADK's Agent class, Runner, and InMemorySessionService to orchestrate 4 agents in sequence. Tools are plain Python functions — no decorators needed. The ADK runner handles tool calling loops via run_async().",
    features: [
      "Gemini 2.0 Flash model integration",
      "ADK Agent() with instruction + plain function tools",
      "Runner + InMemorySessionService for session management",
      "run_async() streams events including tool calls and final responses",
      "Real Wikipedia data fetching via tool execution",
      "Structured memo formatting via format_memo tool",
    ],
    architecture:
      "Researcher Agent → Analyzer Agent → Writer Agent → QA/Review Agent. Each agent gets a fresh session. The orchestrator passes each agent's final response as context to the next. ADK Runner manages tool calling loops internally.",
    agents: [
      { name: "Researcher", role: "Fetches company data from Wikipedia" },
      { name: "Analyzer", role: "Calculates metrics and scores the opportunity" },
      { name: "Writer", role: "Drafts a 2-page investment memo from research + analysis" },
      { name: "QA/Review", role: "Fact-checks memo against research, flags hallucinations" },
    ],
  },
};

export const sdkList = Object.values(sdks);
