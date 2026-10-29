"""Minimal OpenRouter client using only the standard library."""

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://openrouter.ai/api/v1/chat/completions"


def load_key():
    """Read OPENROUTER_API_KEY from the environment, falling back to a .env file at the repo root."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    env = Path(__file__).resolve().parent.parent / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("Set OPENROUTER_API_KEY or put it in .env (see .env.example).")


def chat(model, prompt, max_tokens=200, temperature=0):
    """Send one user message and return the reply text plus usage and latency."""
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "usage": {"include": True},
    }).encode()
    req = urllib.request.Request(API_URL, data=body, headers={
        "Authorization": f"Bearer {load_key()}",
        "Content-Type": "application/json",
    })
    start = time.time()
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.load(resp)
            break
        except urllib.error.HTTPError as e:
            # Free models are rate limited; wait and retry on 429.
            if e.code != 429 or attempt == 7:
                raise
            time.sleep(30 * (attempt + 1))
    usage = data.get("usage", {})
    return {
        "model": model,
        "reply": (data["choices"][0]["message"].get("content") or "").strip(),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "cost_usd": usage.get("cost"),
        "seconds": round(time.time() - start, 2),
    }
