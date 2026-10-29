"""Week 4: make the same API calls through OpenRouter to two models and save the outputs."""

import json
from pathlib import Path

from openrouter import chat

MODELS = [
    "google/gemma-4-31b-it:free",       # open-weight, dense, 31B parameters
    "google/gemma-4-26b-a4b-it:free",   # open-weight, mixture of experts, 26B total / 4B active
]

PROMPTS = [
    "In one sentence, what is model interpretability?",
    "A loan model denies an applicant. Give one reason a post-hoc explanation of that decision "
    "could be misleading. Answer in two sentences.",
]

OUT = Path(__file__).parent / "outputs" / "api_calls.json"


def main():
    # Resume from earlier runs: free models get rate limited, so keep what already worked.
    results = json.loads(OUT.read_text()) if OUT.exists() else []
    done = {(r["model"], r["prompt"]) for r in results}
    for model in MODELS:
        for prompt in PROMPTS:
            if (model, prompt) in done:
                continue
            r = chat(model, prompt, max_tokens=1500)
            r["prompt"] = prompt
            results.append(r)
            OUT.write_text(json.dumps(results, indent=2))
            print(f"[{model}] {r['seconds']}s, {r['completion_tokens']} tokens, ${r['cost_usd']}")
            print(f"  {r['reply']}\n")
    total = sum(r["cost_usd"] or 0 for r in results)
    print(f"{len(results)} calls, total cost ${total:.6f}, saved to {OUT}")


if __name__ == "__main__":
    main()
