"""
fetch_sports_stats.py — Fetch standings and recent results via API-Sports
Usage: python tools/fetch_sports_stats.py "Premier League"
Output: .tmp/stats.json

Supported competitions (add more to LEAGUE_MAP as needed):
Football: Premier League, La Liga, Bundesliga, Serie A, Ligue 1,
          Champions League, Europa League, MLS, Eredivisie, Liga Portugal
"""

import sys
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

API_SPORTS_KEY = os.getenv("API_SPORTS_KEY")
if not API_SPORTS_KEY:
    print("ERROR: API_SPORTS_KEY not set in .env")
    sys.exit(1)

LEAGUE_MAP = {
    # Football (soccer)
    "premier league": {"id": 39, "sport": "football", "season_offset": 0},
    "la liga": {"id": 140, "sport": "football", "season_offset": 0},
    "bundesliga": {"id": 78, "sport": "football", "season_offset": 0},
    "serie a": {"id": 135, "sport": "football", "season_offset": 0},
    "ligue 1": {"id": 61, "sport": "football", "season_offset": 0},
    "champions league": {"id": 2, "sport": "football", "season_offset": 0},
    "europa league": {"id": 3, "sport": "football", "season_offset": 0},
    "mls": {"id": 253, "sport": "football", "season_offset": 0},
    "eredivisie": {"id": 88, "sport": "football", "season_offset": 0},
    "liga portugal": {"id": 94, "sport": "football", "season_offset": 0},
    "primeira liga": {"id": 94, "sport": "football", "season_offset": 0},
}

FOOTBALL_BASE = "https://v3.football.api-sports.io"

def get_headers():
    return {
        "x-apisports-key": API_SPORTS_KEY,
        "x-rapidapi-key": API_SPORTS_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io",
    }

def get_season(offset: int = 0) -> int:
    now = datetime.now()
    year = now.year
    # Most European leagues run Aug-May, so current season started last year if before July
    if now.month < 7:
        year -= 1
    return year + offset

def fetch_standings(league_id: int, season: int) -> list:
    url = f"{FOOTBALL_BASE}/standings"
    resp = requests.get(url, headers=get_headers(), params={"league": league_id, "season": season}, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    standings = []
    try:
        groups = data["response"][0]["league"]["standings"]
        for group in groups:
            for entry in group:
                team = entry["team"]
                all_stats = entry["all"]
                standings.append({
                    "rank": entry["rank"],
                    "team": team["name"],
                    "logo": team.get("logo", ""),
                    "played": all_stats["played"],
                    "won": all_stats["win"],
                    "drawn": all_stats["draw"],
                    "lost": all_stats["lose"],
                    "goals_for": all_stats["goals"]["for"],
                    "goals_against": all_stats["goals"]["against"],
                    "goal_diff": entry["goalsDiff"],
                    "points": entry["points"],
                    "form": entry.get("form", ""),
                    "description": entry.get("description", ""),
                })
    except (KeyError, IndexError) as e:
        print(f"Warning: Could not parse standings: {e}")

    return standings

def fetch_recent_fixtures(league_id: int, season: int, last: int = 6) -> list:
    url = f"{FOOTBALL_BASE}/fixtures"
    resp = requests.get(url, headers=get_headers(),
                        params={"league": league_id, "season": season, "last": last},
                        timeout=20)
    resp.raise_for_status()
    data = resp.json()

    fixtures = []
    for fix in data.get("response", []):
        teams = fix["teams"]
        goals = fix["goals"]
        fixture_info = fix["fixture"]
        fixtures.append({
            "date": fixture_info["date"],
            "home_team": teams["home"]["name"],
            "away_team": teams["away"]["name"],
            "home_goals": goals["home"],
            "away_goals": goals["away"],
            "home_winner": teams["home"].get("winner"),
            "status": fixture_info["status"]["long"],
            "venue": fixture_info.get("venue", {}).get("name", ""),
        })

    # Sort by date descending
    fixtures.sort(key=lambda x: x["date"], reverse=True)
    return fixtures

def fetch_top_scorers(league_id: int, season: int, limit: int = 8) -> list:
    url = f"{FOOTBALL_BASE}/players/topscorers"
    resp = requests.get(url, headers=get_headers(),
                        params={"league": league_id, "season": season},
                        timeout=20)
    resp.raise_for_status()
    data = resp.json()

    scorers = []
    for item in data.get("response", [])[:limit]:
        player = item["player"]
        stats = item["statistics"][0]
        scorers.append({
            "name": player["name"],
            "team": stats["team"]["name"],
            "goals": stats["goals"]["total"] or 0,
            "assists": stats["goals"]["assists"] or 0,
            "photo": player.get("photo", ""),
        })

    return scorers


def fetch_stats(competition: str) -> dict:
    key = competition.lower().strip()
    league_info = LEAGUE_MAP.get(key)

    if not league_info:
        print(f"ERROR: Competition '{competition}' not found in LEAGUE_MAP.")
        print(f"Available: {', '.join(LEAGUE_MAP.keys())}")
        sys.exit(1)

    league_id = league_info["id"]
    season = get_season(league_info["season_offset"])
    print(f"Fetching stats for {competition} (league_id={league_id}, season={season})")

    standings = fetch_standings(league_id, season)
    print(f"  Standings: {len(standings)} teams")

    fixtures = fetch_recent_fixtures(league_id, season)
    print(f"  Recent fixtures: {len(fixtures)}")

    top_scorers = fetch_top_scorers(league_id, season)
    print(f"  Top scorers: {len(top_scorers)}")

    output = {
        "competition": competition,
        "league_id": league_id,
        "season": season,
        "fetched_at": datetime.now().isoformat(),
        "standings": standings,
        "recent_fixtures": fixtures,
        "top_scorers": top_scorers,
    }

    os.makedirs(".tmp", exist_ok=True)
    out_path = ".tmp/stats.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Saved to {out_path}")
    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/fetch_sports_stats.py 'Premier League'")
        sys.exit(1)
    competition = " ".join(sys.argv[1:])
    fetch_stats(competition)
