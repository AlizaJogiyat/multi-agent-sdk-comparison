# Simple 2-Agent System

A minimal implementation of a 2-agent system using the Anthropic Claude API with the agentic loop pattern.

## System Overview

**Agent 1 - Researcher**: Searches for company information
- Tools: `search_company_info`
- Output: Research brief with company data

**Agent 2 - Analyzer**: Analyzes research and scores opportunities
- Tools: `calculate_metric`, `score_opportunity`
- Input: Agent 1's research output
- Output: Investment analysis and opportunity score

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API key**:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

## Usage

Run the complete pipeline:
```bash
python agent_system.py
```

## Output Format

The script displays:
- **Agent 1 iterations**: Shows tool calls to `search_company_info`
- **Agent 1 research findings**: Company data and summary
- **Agent 2 iterations**: Shows tool calls to `calculate_metric` and `score_opportunity`
- **Agent 2 analysis**: Investment recommendation and scoring
- **Final results**: Both agent outputs combined

### Example Output Structure

```
AGENT 1: RESEARCHER
Task: Research company information for 'Vettio'

Iteration 1:
  Stop Reason: tool_use
  → Calling tool: search_company_info
  Tool Input: {"company_name": "Vettio"}
  Tool Result: {...}

Iteration 2:
  Stop Reason: end_turn
  Final Output: [Research summary from Agent 1]

AGENT 2: ANALYZER
Task: Analyze the research and score the opportunity

Iteration 1:
  Stop Reason: tool_use
  → Calling tool: calculate_metric
  Tool Result: {...}

Iteration 2:
  Stop Reason: tool_use
  → Calling tool: score_opportunity
  Tool Result: {...}

Iteration 3:
  Stop Reason: end_turn
  Final Output: [Analysis from Agent 2]
```

## Key Features

- **Agentic Loop Pattern**: Both agents run tool_use → execute → repeat until end_turn
- **Data Passing**: Agent 1's output is passed as context to Agent 2
- **Real Data Fetching**: Fetches actual company data from Wikipedia
  - Extracts founding year, sector, headquarters from Wikipedia articles
  - Falls back gracefully if company not found
- **Clear Logging**: Shows iteration numbers, stop reasons, and tool calls
- **Separation of Concerns**: Independent agent functions that can be reused

## Data Sources

The system fetches **real company data** from:
- **Wikipedia API**: Primary source for company information
  - Extracts: Founded year, sector, headquarters, description
  - Automatic fallback if company not found
- **Web Scraping**: Backup data extraction
  - Parses Wikipedia articles for structured info
  - Auto-detects sector keywords
  - Extracts location patterns

## Customization

### Run with different company

The script prompts for company name:
```
Enter company name to research: OpenAI
```

Or any company with a Wikipedia page (e.g., Apple, Microsoft, Tesla, etc.)

### Add custom company data (optional)

If you want to override Wikipedia data or add companies not on Wikipedia, create a `companies_cache.json`:
```json
{
  "Vettio": {
    "founded": 2020,
    "revenue": "$5.2M",
    "employees": 45,
    "sector": "AI - Recruitment & HR Tech",
    "headquarters": "San Francisco, CA",
    "description": "AI-powered recruitment platform"
  }
}
```

Then modify `execute_search_company_info()` to check this file first.

## Architecture Notes

- **Messages structure**: Follows Anthropic SDK pattern with role/content
- **Tool execution**: Centralized in `process_tool_call()` for easy mocking
- **State management**: Each agent maintains its own message history
- **No external APIs**: All tool results are simulated for reliable testing
