"""
render_html.py — Render final sports brief HTML from collected data
Usage: python tools/render_html.py
Reads:  .tmp/stats.json, .tmp/news.json, .tmp/narrative.json
Output: .tmp/sports_brief_{competition}_{date}.html

narrative.json schema (Claude writes this):
{
  "headline": "string",
  "intro": "string",
  "stories": [
    {
      "title": "string",
      "body": "string",
      "source": "string",
      "url": "string",
      "tag": "string"   // e.g. "Match Report", "Transfer", "Injury"
    }
  ],
  "key_storylines": ["string", ...],
  "stat_highlights": [
    {"label": "string", "value": "string", "context": "string"}
  ]
}
"""

import json
import os
import sys
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


def load_json(path: str) -> dict:
    if not os.path.exists(path):
        print(f"ERROR: {path} not found. Run the fetch tools first.")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def form_badges(form_string: str) -> list:
    """Convert form string like 'WWDLW' into list of dicts with result + css class."""
    if not form_string:
        return []
    mapping = {"W": "win", "D": "draw", "L": "loss"}
    return [{"result": c, "cls": mapping.get(c, "unknown")} for c in form_string[-5:]]


def render(stats_path=".tmp/stats.json",
           news_path=".tmp/news.json",
           narrative_path=".tmp/narrative.json") -> str:

    stats = load_json(stats_path)
    news = load_json(news_path)
    narrative = load_json(narrative_path)

    # Enrich standings with form badges
    for team in stats.get("standings", []):
        team["form_badges"] = form_badges(team.get("form", ""))

    # Prepare Chart.js datasets
    scorers_labels = [s["name"].split(" ")[-1] for s in stats.get("top_scorers", [])]
    scorers_data = [s["goals"] for s in stats.get("top_scorers", [])]
    scorers_teams = [s["team"] for s in stats.get("top_scorers", [])]

    # Top 8 teams by points for mini standings chart
    top8 = stats.get("standings", [])[:8]
    standings_labels = [t["team"] for t in top8]
    standings_points = [t["points"] for t in top8]

    competition = stats["competition"]
    date_str = datetime.now().strftime("%B %d, %Y")
    slug = competition.lower().replace(" ", "_")
    output_filename = f".tmp/sports_brief_{slug}_{datetime.now().strftime('%Y%m%d')}.html"

    env = Environment(loader=FileSystemLoader("tools/templates"))
    template = env.get_template("sports_brief.html")

    html = template.render(
        competition=competition,
        date_str=date_str,
        season=stats.get("season"),
        narrative=narrative,
        standings=stats.get("standings", [])[:20],
        fixtures=stats.get("recent_fixtures", [])[:8],
        top_scorers=stats.get("top_scorers", []),
        articles=news.get("articles", [])[:6],
        # Chart data (JSON-serialized for injection into JS)
        scorers_labels=json.dumps(scorers_labels),
        scorers_data=json.dumps(scorers_data),
        scorers_teams=json.dumps(scorers_teams),
        standings_labels=json.dumps(standings_labels),
        standings_points=json.dumps(standings_points),
    )

    os.makedirs(".tmp", exist_ok=True)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Rendered: {output_filename}")
    return output_filename


if __name__ == "__main__":
    output = render()
    print(f"\nOpen in browser: {os.path.abspath(output)}")
