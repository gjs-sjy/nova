"""
assistant.py — asks an LLM (through OpenRouter) to explain a function in plain English.

Python already worked out the facts (callers, what could break). The AI only
puts those facts into words. We send ONLY:
  - the function's code
  - its direct callers
  - all affected functions (what could break)
  - what it calls
Never the whole codebase.

Settings live in backend/.env (never commit it):
    OPENROUTER_API_KEY=sk-or-...
    OPENROUTER_MODEL=some/model-name
"""

import os

import httpx
from dotenv import load_dotenv

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")

SYSTEM_PROMPT = """You explain Python code to a developer who is new to this codebase.
Rules:
- Answer in 3 to 5 short sentences of plain English.
- Only use the code and dependency data you are given. Never invent functions, calls, or callers.
- Refer to functions by name."""

IMPACT_EXTRA = """- The user is asking what could break if this function were deleted.
  Name the functions that would be affected, starting with the direct callers.
- Say clearly that this is a static-analysis risk estimate, not a guarantee:
  dynamic calls, decorators, or code outside this project can hide dependencies."""


def format_ids(ids):
    return "\n".join(f"- {node_id}" for node_id in ids) if ids else "- (none)"


def build_user_message(node, impact, mode):
    """The context we send to the AI: one function's code plus its dependency facts."""
    question = (
        "What does this function do?"
        if mode == "explain"
        else "What could break if I delete this function?"
    )
    return f"""Function: {node["id"]}
File: {node["file"]} (lines {node["start_line"]}-{node["end_line"]})

Code:
```python
{node["code"]}```

Direct callers (functions that call it):
{format_ids(impact["direct_callers"])}

All affected (everything that depends on it, directly or indirectly):
{format_ids(impact["all_affected"])}

What it calls:
{format_ids(impact["calls"])}

Question: {question}"""


async def explain(node, impact, mode):
    """Return a plain-English answer. On any failure, return a friendly message instead of crashing."""
    # Re-read .env every time, so editing it doesn't need a server restart.
    load_dotenv(ENV_PATH, override=True)
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv("OPENROUTER_MODEL", "").strip()

    if not api_key or api_key == "your-key-here":
        return "The AI isn't set up yet: add OPENROUTER_API_KEY to backend/.env."
    if not model:
        return "The AI isn't set up yet: add OPENROUTER_MODEL to backend/.env."

    system = SYSTEM_PROMPT + ("\n" + IMPACT_EXTRA if mode == "impact" else "")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                OPENROUTER_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": build_user_message(node, impact, mode)},
                    ],
                },
            )
        data = response.json()
        if response.status_code != 200:
            # OpenRouter explains what went wrong (bad key, unknown model, no credits...).
            reason = data.get("error", {}).get("message", f"HTTP {response.status_code}")
            return f"Sorry, the AI request failed: {reason}"
        return data["choices"][0]["message"]["content"].strip()
    except httpx.TimeoutException:
        return "Sorry, the AI took too long to answer. Please try again."
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError, AttributeError):
        return "Sorry, the AI couldn't be reached right now. Please try again."
