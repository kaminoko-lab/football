# Workflow: Sports News Brief

## Objective
Generate a fully-rendered HTML sports news brief for a given competition, including real-time standings, recent results, top scorers, curated news articles, and Chart.js infographics.

## Inputs
- `competition` (required): Competition name, e.g. "Premier League", "La Liga", "Champions League"

## Supported Competitions
See `LEAGUE_MAP` in `tools/fetch_sports_stats.py` for the full list.
To add a new competition: find its ID on [API-Sports](https://www.api-sports.io/), add it to the dict.

## Required API Keys (set in `.env`)
```
TAVILY_API_KEY=your_key
API_SPORTS_KEY=your_key
```
- Tavily: https://app.tavily.com — free tier: 1,000 searches/month
- API-Sports: https://dashboard.api-sports.io — free tier: 100 requests/day

## Required Libraries
```bash
pip install requests python-dotenv jinja2
```

---

## Steps

### Step 1 — Fetch live stats
```bash
python tools/fetch_sports_stats.py "Premier League"
```
- Fetches: standings, last 6 results, top 8 scorers
- Output: `.tmp/stats.json`
- Failure modes:
  - `Competition not found`: Check spelling against LEAGUE_MAP keys
  - `401 Unauthorized`: Check API_SPORTS_KEY in .env
  - `API rate limit`: Free tier = 100 req/day. If hit, use cached `.tmp/stats.json` from previous run.

### Step 2 — Fetch news articles
```bash
python tools/fetch_news.py "Premier League"
```
- Fetches last 48h articles from trusted sports domains
- Output: `.tmp/news.json`
- Failure modes:
  - `401`: Check TAVILY_API_KEY
  - `0 articles returned`: Broaden query or increase `days_back` parameter in the script

### Step 3 — Write narrative (Claude's job)
Read `.tmp/stats.json` and `.tmp/news.json`, then write `.tmp/narrative.json`.

**narrative.json schema:**
```json
{
  "headline": "Catchy, specific headline (e.g. 'Arsenal's Title Push Continues as City Drop Points')",
  "intro": "2–3 sentence summary of the week's key narrative. Hook the reader.",
  "stories": [
    {
      "title": "Story headline",
      "body": "2–3 sentences. Focused on one key event/development.",
      "source": "BBC Sport",
      "url": "https://...",
      "tag": "Match Report | Transfer | Injury | Tactics | Preview"
    }
  ],
  "key_storylines": [
    "One-liner about a trend or subplot worth watching",
    "Another storyline (aim for 3–5 total)"
  ],
  "stat_highlights": [
    {
      "label": "Short label",
      "value": "Bold number or short phrase",
      "context": "One line of context (optional)"
    }
  ]
}
```

**Writing guidelines:**
- Headline: specific > generic. Name teams/players. Avoid "Roundup" or "Week in Review".
- Stories: prioritise biggest results, then transfers, then injury news.
- stat_highlights: pull 3–5 from the stats data. Interesting angles beat obvious ones.
  - Good: "Haaland: 1 goal every 73 mins"
  - Weak: "Top scorer has 18 goals"
- key_storylines: forward-looking where possible. What should we watch next week?

### Step 4 — Render HTML
```bash
python tools/render_html.py
```
- Reads: `.tmp/stats.json`, `.tmp/news.json`, `.tmp/narrative.json`
- Output: `.tmp/sports_brief_{competition}_{YYYYMMDD}.html`
- Open in browser to review

---

## Output
A self-contained HTML file with:
- Hero header with headline + intro
- Stat highlight cards
- Top stories grid (3 columns)
- Key storylines panel
- Standings table with form badges
- Recent results grid
- Bar chart: top scorers
- Bar chart: top 8 teams by points

---

## Edge Cases & Known Issues

### No articles returned by Tavily
- Increase `days_back` from 2 to 5 in `fetch_news.py`
- Remove domain whitelist to cast wider net (edit `TRUSTED_DOMAINS` to `[]`)

### API-Sports free tier (100 req/day)
- Each run uses ~3 requests (standings + fixtures + top scorers)
- If rate limited, skip Step 1 and use existing `.tmp/stats.json`

### Cup competitions (Champions League, etc.)
- Standings may be empty mid-competition (group stage vs knockout)
- Recent fixtures will still work; template handles empty standings gracefully

### Season detection
- `get_season()` assumes European calendar (season starts July/Aug)
- For leagues with different calendars (MLS, Copa América), adjust `season_offset` in LEAGUE_MAP

---

## Future Improvements
- Add player spotlight section (fetch player stats for a named player)
- Add next-fixture preview with form analysis
- Google Drive upload via existing credentials.json
- Multi-competition digest (run for 3 leagues and merge into one brief)
- PDF export via WeasyPrint or Puppeteer
