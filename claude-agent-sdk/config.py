import os
import sys

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
DEFAULT_COMPANY = os.environ.get("DEFAULT_COMPANY", "Stripe")
MAX_REVISION_CYCLES = 3
MAX_WRITER_VALIDATION_RETRIES = 3
MEMO_MIN_WORDS = 800
MEMO_MAX_WORDS = 1200
MEMO_REQUIRED_SECTIONS = [
    "Executive Summary",
    "Company Overview",
    "Financial Analysis",
    "Risk Assessment",
    "Recommendation",
]


def validate_config():
    """Validate required configuration. Exits with clear error if missing."""
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY is missing or invalid", file=sys.stderr)
        sys.exit(1)
