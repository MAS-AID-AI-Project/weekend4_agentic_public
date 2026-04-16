"""
Galactic Betting UI Components
React-style component architecture for HTML/CSS generation.
"""

from .templates import (
    render_page,
    render_header,
    render_standings_table,
    render_bracket,
    render_completed_matches,
    render_upcoming_matches,
    render_bets_sidebar,
    render_bet_form,
    render_modal,
    get_logo_img,
    get_bracket_team,
)

__all__ = [
    'render_page',
    'render_header',
    'render_standings_table',
    'render_bracket',
    'render_completed_matches',
    'render_upcoming_matches',
    'render_bets_sidebar',
    'render_bet_form',
    'render_modal',
    'get_logo_img',
    'get_bracket_team',
]
