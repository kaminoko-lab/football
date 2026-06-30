# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## The WAT Framework

This repo uses the **WAT architecture** (Workflows, Agents, Tools) — probabilistic AI handles reasoning/orchestration while deterministic Python scripts handle execution.

- **Workflows** (`workflows/`): Markdown SOPs defining objectives, inputs, tool sequences, outputs, and edge cases
- **Agent** (you): Read the relevant workflow, run tools in order, handle failures, ask clarifying questions
- **Tools** (`tools/`): Python scripts that do the actual work — API calls, data transforms, rendering

**Key principle:** Don't do execution work directly. Check `tools/` for an existing script first. Only create new tools when nothing exists for the task.

## Commands

### Dependencies
```bash
pip install requests python-dotenv jinja2 Pillow
```

### Running Tools
All tools are run from the project root:
```bash
python tools/fetch_sports_stats.py "Premier League"   # -> .tmp/stats.json
python tools/fetch_news.py "Premier League"            # -> .tmp/news.json
python tools/render_html.py                            # -> .tmp/sports_brief_{slug}_{date}.html
python tools/make_water_bottle.py                      # -> .tmp/kaminoko_water_bottle.png
```

Tools accept inputs via CLI args, load credentials from `.env`, output JSON to stdout/`.tmp/`, and exit non-zero on failure.

## Data Flow

The sports news workflow (see `workflows/sports_news.md`) is a 4-step pipeline:

1. `fetch_sports_stats.py` -> `.tmp/stats.json` (standings, fixtures, top scorers from API-Sports)
2. `fetch_news.py` -> `.tmp/news.json` (curated articles from Tavily)
3. **You write** `.tmp/narrative.json` (headline, intro, stories, key_storylines, stat_highlights — see schema in workflow)
4. `render_html.py` reads all three `.tmp/*.json` files -> renders Jinja2 template at `tools/templates/sports_brief.html`

Step 3 is the only non-deterministic step — you synthesize the data into editorial content. The `narrative.json` schema and writing guidelines are defined in `workflows/sports_news.md`.

## API Keys

Set in `.env` (never committed):
- `TAVILY_API_KEY` — news search (free tier: 1,000 searches/month)
- `API_SPORTS_KEY` — sports data (free tier: 100 requests/day, ~3 per run)

## Operational Rules

- **Check before spending:** If a tool uses paid API calls or credits, confirm with the user before re-running after failures.
- **Don't overwrite workflows** without asking — they are curated SOPs, not disposable scaffolding.
- **Update workflows** when you discover rate limits, timing quirks, or better approaches.
- **Deliverables** go to cloud services (Google Sheets, Slides, etc.), not local files. Everything in `.tmp/` is disposable intermediate data.
- **Self-improvement loop:** When something breaks — fix the tool, verify the fix, update the workflow, move on.

## Supported Competitions

Defined in `LEAGUE_MAP` in `tools/fetch_sports_stats.py`: Premier League, La Liga, Bundesliga, Serie A, Ligue 1, Champions League, Europa League, MLS, Eredivisie, Liga Portugal. To add a new one, find its ID on API-Sports and add it to the dict.
