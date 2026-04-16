# Galactic Betting Module
# This module provides the backend and frontend for the Intergalactic Football Betting scenario

from .data import (
    TEAMS,
    TEAM_LOGOS,
    REGULAR_SEASON_RESULTS,
    PLAYOFF_MATCHES,
    UPCOMING_MATCHES,
    PAPARAZZI_NEWS,
    get_team_standings,
    get_match_by_id,
)

from .tools import (
    search_paparazzi_news,
    get_match_history,
    get_betting_odds,
    place_bet,
    get_all_tools,
)

from .backend import (
    start_servers,
    start_betting_server,
    start_news_server,
    stop_servers,
    force_kill_ports,
    display_in_colab,
    get_wallet_balance,
    reset_wallet,
    reveal_results,
    get_placed_bets,
)

__all__ = [
    # Data
    'TEAMS',
    'TEAM_LOGOS',
    'REGULAR_SEASON_RESULTS',
    'PLAYOFF_MATCHES',
    'UPCOMING_MATCHES',
    'PAPARAZZI_NEWS',
    'get_team_standings',
    'get_match_by_id',
    # Tools
    'search_paparazzi_news',
    'get_match_history',
    'get_betting_odds',
    'place_bet',
    'get_all_tools',
    # Backend
    'start_servers',
    'start_betting_server',
    'start_news_server',
    'stop_servers',
    'force_kill_ports',
    'display_in_colab',
    'get_wallet_balance',
    'reset_wallet',
    'reveal_results',
    'get_placed_bets',
]
