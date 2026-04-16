"""
LangChain Tools for Galactic Betting
These tools allow agents to interact with the betting system.
"""

from typing import List, Dict
from langchain.tools import tool

from .data import (
    get_all_completed_matches,
    get_upcoming_matches_for_betting,
    search_news as _search_news,
    TEAMS,
    TEAM_LOGOS,
)
from .backend import place_bet_internal, get_wallet_balance


def _clean_input(value: str) -> str:
    """Helper to clean common LLM formatting issues from input strings."""
    value = value.strip()
    # Remove quotes if present
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    return value


@tool
def search_paparazzi_news(keywords: str) -> List[Dict]:
    """
    Search through StarScoop paparazzi news articles for relevant information.

    Use this tool to find gossip, rumors, and insider information about teams and players
    that might affect match outcomes.

    IMPORTANT: This uses strict keyword matching. Use only 1-2 simple keywords for best results.
    Search for a team name OR a single topic, not both together.

    Args:
        keywords: Just the search terms, nothing else. Examples: 'Meteor Mavericks' or 'injury' or 'goalkeeper'.
                  Do NOT include 'keywords=' or quotes.

    Returns:
        List of matching news articles with date, headline, content, and tags.
        Returns empty list if no matches found.
    """
    # Clean up common LLM formatting issues
    keywords = _clean_input(keywords)
    # Remove any 'keywords=' prefix the LLM might add
    if keywords.lower().startswith('keywords='):
        keywords = keywords[9:]
        keywords = _clean_input(keywords)

    results = _search_news(keywords)
    return results


@tool
def get_match_history(team_name: str) -> Dict:
    """
    Get historical match results from the regular season and completed playoff matches.

    Use this tool to analyze team performance, win/loss records, and scoring patterns.
    This helps understand which teams are in good form and which are struggling.

    Args:
        team_name: Just the team name, nothing else. Use 'all' to get all matches.
                   Examples: 'Stellar Strikers' or 'Meteor Mavericks' or 'all'.
                   Do NOT include 'team_name=' or quotes.
                   Valid teams: Andromeda Asteroids, Nebula Nomads, Cosmic Crusaders,
                   Stellar Strikers, Galaxy Giants, Meteor Mavericks, Quasar Queens, Pulsar Pirates

    Returns:
        Dictionary containing:
        - matches: List of match results with date, teams, scores, and winner
        - summary: If team_name provided (not 'all'), includes win/loss/draw record
    """
    # Clean up common LLM formatting issues
    team_name = _clean_input(team_name)
    # Remove any 'team_name=' prefix the LLM might add
    if team_name.lower().startswith('team_name='):
        team_name = team_name[10:]
        team_name = _clean_input(team_name)

    all_matches = get_all_completed_matches()

    # Handle 'all' case - return all matches without filtering
    if team_name.strip().lower() == 'all':
        return {
            "total_matches": len(all_matches),
            "matches": all_matches
        }

    # Validate team name
    if team_name not in TEAMS:
        return {
            "error": f"Unknown team: {team_name}",
            "valid_teams": TEAMS
        }

    # Filter matches for this team
    team_matches = [
        m for m in all_matches
        if m["home"] == team_name or m["away"] == team_name
    ]

    # Calculate record
    wins = sum(1 for m in team_matches if m["winner"] == team_name)
    draws = sum(1 for m in team_matches if m["winner"] == "Draw")
    losses = len(team_matches) - wins - draws

    # Goals scored/conceded
    goals_for = sum(
        m["home_score"] if m["home"] == team_name else m["away_score"]
        for m in team_matches
    )
    goals_against = sum(
        m["away_score"] if m["home"] == team_name else m["home_score"]
        for m in team_matches
    )

    return {
        "team": team_name,
        "logo": TEAM_LOGOS.get(team_name, ""),
        "matches": team_matches,
        "summary": {
            "total_matches": len(team_matches),
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": goals_for - goals_against
        }
    }


@tool
def get_betting_odds() -> List[Dict]:
    """
    Get current betting odds for all upcoming matches.

    Use this tool to see which matches are available for betting and what the
    bookmakers' odds are for each outcome. Lower odds mean the team is favored to win.

    Returns:
        List of upcoming matches with:
        - match_id: Unique identifier for placing bets
        - round: Tournament round (e.g., "Upper Bracket Final")
        - date: Match date
        - home: Home team name
        - away: Away team name
        - odds: Dictionary with odds for home win, away win, and draw
    """
    matches = get_upcoming_matches_for_betting()

    # Add wallet balance for context
    balance = get_wallet_balance()

    return {
        "current_balance": balance,
        "upcoming_matches": matches,
        "note": "Use place_bet tool with match_id, team_to_win, and amount to place bets"
    }


@tool
def place_bet(bet_details: str) -> Dict:
    """
    Place a bet on an upcoming playoff match.

    Use this tool to bet Galactic Credits on match outcomes. Your potential
    winnings are calculated as: amount * odds.

    Note: Playoff matches cannot end in a draw - they go to penalties if needed.
    You can only bet on one of the two teams to win.

    Args:
        bet_details: Three comma-separated values: match_id, team_to_win, amount.
                     Examples: '201, Stellar Strikers, 100' or '202, Meteor Mavericks, 50'.
                     Do NOT use keyword=value format. Just provide the three values separated by commas.

    Returns:
        Success: Confirmation with bet details and potential winnings
        Error: Error message explaining why the bet failed
    """
    import re

    # Clean up common LLM formatting issues - handle keyword=value format
    # e.g., "match_id=201, team_to_win=Stellar Strikers, amount=100"
    bet_details = bet_details.strip()

    # Check if the LLM used keyword=value format and extract values
    if 'match_id=' in bet_details.lower() or 'team_to_win=' in bet_details.lower() or 'amount=' in bet_details.lower():
        # Try to extract values from keyword=value format
        match_id_match = re.search(r'match_id\s*=\s*(\d+)', bet_details, re.IGNORECASE)
        team_match = re.search(r'team_to_win\s*=\s*["\']?([^,"\'\d][^,"\']*?)["\']?\s*(?:,|$)', bet_details, re.IGNORECASE)
        amount_match = re.search(r'amount\s*=\s*(\d+(?:\.\d+)?)', bet_details, re.IGNORECASE)

        if match_id_match and team_match and amount_match:
            try:
                match_id = int(match_id_match.group(1))
                team_to_win = team_match.group(1).strip()
                amount = float(amount_match.group(1))
                result = place_bet_internal(match_id, team_to_win, amount)
                return result
            except ValueError:
                pass  # Fall through to regular parsing

    # Parse the comma-separated input
    parts = bet_details.split(",")
    if len(parts) != 3:
        return {
            "error": "Invalid format. Please provide 'match_id, team_to_win, amount' (e.g., '201, Stellar Strikers, 100')"
        }

    try:
        match_id = int(_clean_input(parts[0]))
        team_to_win = _clean_input(parts[1])
        amount = float(_clean_input(parts[2]))
    except ValueError as e:
        return {
            "error": f"Invalid values. match_id must be integer, amount must be number. Error: {str(e)}"
        }

    result = place_bet_internal(match_id, team_to_win, amount)
    return result


def get_all_tools() -> List:
    """Get all LangChain tools for the betting agent."""
    return [
        search_paparazzi_news,
        get_match_history,
        get_betting_odds,
        place_bet
    ]
