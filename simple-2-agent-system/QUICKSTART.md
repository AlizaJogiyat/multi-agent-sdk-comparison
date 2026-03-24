# Quick Start Guide

## 30-Second Setup

```bash
# 1. Navigate to the folder
cd /home/aleeza/Desktop/code/projects/multi-agent-sdk-comparison/simple-2-agent-system

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 5. Run the system
python agent_system.py
```

## What Happens When You Run It

1. **Agent 1 (Researcher)** activates:
   - Calls `search_company_info` tool for "Vettio"
   - Returns company data (founded, revenue, employees, sector)
   - Compiles research brief

2. **Agent 2 (Analyzer)** receives Agent 1's output:
   - Calls `calculate_metric` to compute revenue/employee
   - Calls `score_opportunity` to rate investment
   - Provides recommendation

3. **Final Output** shows both agents' work together

## Expected Output Pattern

```
AGENT 1: RESEARCHER
Task: Research company information for 'Vettio'

Iteration 1:
  Stop Reason: tool_use
  → Calling tool: search_company_info
  Tool Input: {"company_name": "Vettio"}
  Tool Result: {"success": true, "data": {...}}

Iteration 2:
  Stop Reason: end_turn
  Final Output: [Research findings...]

AGENT 2: ANALYZER
Task: Analyze the research and score the opportunity

Iteration 1:
  Stop Reason: tool_use
  → Calling tool: calculate_metric
  ...
```

## Troubleshooting

**ImportError: No module named 'anthropic'**
- Run: `pip install -r requirements.txt`

**"API key not found" error**
- Run: `export ANTHROPIC_API_KEY="your-key-here"`
- Or create `.env` file with `ANTHROPIC_API_KEY=your-key-here`

**Rate limit or connection errors**
- Check your API key is valid
- Check internet connection
- Wait a moment and retry

## Try Different Companies

The system will prompt for input when you run it:

```
Enter company name to research: Apple
```

Try any company with a Wikipedia page:
- **Tech**: Apple, Google, Microsoft, OpenAI, Meta
- **Startups**: Airbnb, Stripe, Figma, Notion
- **Finance**: Tesla, PayPal, Square
- Or any other company!

## Next Steps

- Modify tool definitions in `RESEARCHER_TOOLS` and `ANALYZER_TOOLS`
- Add new companies to `company_data` in `execute_search_company_info()`
- Connect to real APIs instead of simulated tools
- Add more agents to the pipeline
