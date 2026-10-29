# ACM Research Lab 2026–27: Navilan Santhanakrishnan

My work for the [UCSC ACM Research Lab](https://github.com/CantBush/ACM-Research-Lab-26-27), Fall 2026 (AI safety). One folder per week.

| Week | Deliverable | Folder |
| --- | --- | --- |
| 4 | Kickoff: OpenRouter key, API calls to two models, Lipton (2016), paper pick | [`week-4/`](week-4/) |

## Running the code

The code uses only the Python standard library (Python 3.9+).

1. Copy `.env.example` to `.env` and put your OpenRouter key in it. `.env` is gitignored.
   Setting `OPENROUTER_API_KEY` in your shell works too.
2. Run from the week's folder:

```sh
cd week-4
python3 api_calls.py   # same prompts to each model, saved to outputs/api_calls.json
```

The script skips calls whose results are already saved, so a run cut short by a rate limit can be restarted.
