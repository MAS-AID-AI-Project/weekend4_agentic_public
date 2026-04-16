"""
HTML Template Components for Galactic Betting UI.
Each function returns an HTML string for its respective component.
"""

from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime


# CSS files to include
CSS_FILES = [
    'global.css',
    'header.css',
    'card.css',
    'standings.css',
    'bracket.css',
    'matches.css',
    'betting.css',
    'modal.css',
]


def get_logo_img(team: str, size: str, team_logo_files: Dict[str, str]) -> str:
    """Generate an img tag for team logo."""
    logo_file = team_logo_files.get(team, "")
    if logo_file:
        size_class = f"team-logo-{size}"
        return f'<img src="/logos/{logo_file}" alt="{team}" class="{size_class}">'
    return ""


def get_bracket_team(match: Optional[Dict], is_home: bool, team_logo_files: Dict[str, str]) -> str:
    """Generate HTML for a bracket team entry."""
    if not match:
        return '<span class="bracket-team tbd">TBD</span>'

    team = match["home"] if is_home else match["away"]
    logo = get_logo_img(team, "bracket", team_logo_files)

    if "home_score" in match and "away_score" in match:
        score = match["home_score"] if is_home else match["away_score"]
        winner = match.get("winner", "")
        winner_class = "winner" if winner == team else ""
        return f'<span class="bracket-team {winner_class}">{logo}<span class="bracket-team-name">{team}</span><span class="bracket-score {winner_class}">{score}</span></span>'
    else:
        return f'<span class="bracket-team">{logo}<span class="bracket-team-name">{team}</span></span>'


def render_header(wallet_balance: float) -> str:
    """Render the page header with logo and wallet."""
    return f'''
    <div class="header">
        <div class="logo">
            <h1>Galactic<span>Bets</span>.io</h1>
        </div>
        <div class="header-info">
            <div class="current-date">Current Date: <strong>April 18, 2026</strong></div>
            <div class="wallet" id="wallet">{wallet_balance:.2f}</div>
        </div>
    </div>
    '''


def render_standings_table(standings: List[Dict], team_colors: Dict[str, str], team_logo_files: Dict[str, str]) -> str:
    """Render the standings table component."""
    rows = ""
    for s in standings:
        logo_img = get_logo_img(s["team"], "table", team_logo_files)
        color = team_colors.get(s["team"], "#333")
        gd = s["goals_for"] - s["goals_against"]
        gd_str = f"+{gd}" if gd > 0 else str(gd)
        rows += f'''
        <tr>
            <td>{s["rank"]}</td>
            <td class="team-cell">{logo_img}<span style="color:{color};font-weight:600;">{s["team"]}</span></td>
            <td>{s["wins"]}</td>
            <td>{s["draws"]}</td>
            <td>{s["losses"]}</td>
            <td>{s["goals_for"]}</td>
            <td>{s["goals_against"]}</td>
            <td>{gd_str}</td>
            <td><strong>{s["points"]}</strong></td>
        </tr>
        '''

    return f'''
    <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
            <h2>Regular Season Standings</h2>
        </div>
        <div class="card-body">
            <table class="standings-table">
                <tr>
                    <th>#</th>
                    <th>Team</th>
                    <th class="tooltip" data-tip="Wins">W</th>
                    <th class="tooltip" data-tip="Draws">D</th>
                    <th class="tooltip" data-tip="Losses">L</th>
                    <th class="tooltip" data-tip="Goals For">GF</th>
                    <th class="tooltip" data-tip="Goals Against">GA</th>
                    <th class="tooltip" data-tip="Goal Difference">GD</th>
                    <th class="tooltip" data-tip="Points">PTS</th>
                </tr>
                {rows}
            </table>
        </div>
    </div>
    '''


def render_bracket(upcoming_matches: List[Dict], team_logo_files: Dict[str, str]) -> str:
    """Render the tournament bracket component."""
    upcoming_dict = {m["match_id"]: m for m in upcoming_matches}

    return f'''
    <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
            <h2>Playoff Bracket</h2>
        </div>
        <div class="bracket-container">
            <div class="bracket">
                <!-- Upper Bracket Row -->
                <div class="bracket-row">
                    <!-- Upper Bracket R1 -->
                    <div class="bracket-round">
                        <div class="bracket-round-title">Upper Bracket R1</div>
                        <div class="bracket-match upcoming">
                            {get_bracket_team(upcoming_dict.get(101), True, team_logo_files)}
                            <div class="bracket-vs">vs</div>
                            {get_bracket_team(upcoming_dict.get(101), False, team_logo_files)}
                        </div>
                        <div class="bracket-match upcoming">
                            {get_bracket_team(upcoming_dict.get(102), True, team_logo_files)}
                            <div class="bracket-vs">vs</div>
                            {get_bracket_team(upcoming_dict.get(102), False, team_logo_files)}
                        </div>
                    </div>

                    <!-- Upper Bracket Final -->
                    <div class="bracket-round">
                        <div class="bracket-round-title">Upper Final</div>
                        <div class="bracket-match">
                            <span class="bracket-team tbd">TBD</span>
                            <div class="bracket-vs">vs</div>
                            <span class="bracket-team tbd">TBD</span>
                        </div>
                    </div>

                    <!-- Cross Semi -->
                    <div class="bracket-round">
                        <div class="bracket-round-title">Cross Semi</div>
                        <div class="bracket-match">
                            <span class="bracket-team tbd">TBD</span>
                            <div class="bracket-vs">vs</div>
                            <span class="bracket-team tbd">TBD</span>
                        </div>
                    </div>

                    <!-- Grand Final -->
                    <div class="bracket-round">
                        <div class="bracket-round-title">Grand Final</div>
                        <div class="bracket-match">
                            <span class="bracket-team tbd">TBD</span>
                            <div class="bracket-vs">vs</div>
                            <span class="bracket-team tbd">TBD</span>
                        </div>
                    </div>
                </div>

                <!-- Lower Bracket Row -->
                <div class="bracket-row">
                    <!-- Lower Bracket R1 -->
                    <div class="bracket-round">
                        <div class="bracket-round-title">Lower Bracket R1</div>
                        <div class="bracket-match upcoming">
                            {get_bracket_team(upcoming_dict.get(103), True, team_logo_files)}
                            <div class="bracket-vs">vs</div>
                            {get_bracket_team(upcoming_dict.get(103), False, team_logo_files)}
                        </div>
                        <div class="bracket-match upcoming">
                            {get_bracket_team(upcoming_dict.get(104), True, team_logo_files)}
                            <div class="bracket-vs">vs</div>
                            {get_bracket_team(upcoming_dict.get(104), False, team_logo_files)}
                        </div>
                    </div>

                    <!-- Lower Bracket Final -->
                    <div class="bracket-round">
                        <div class="bracket-round-title">Lower Final</div>
                        <div class="bracket-match">
                            <span class="bracket-team tbd">TBD</span>
                            <div class="bracket-vs">vs</div>
                            <span class="bracket-team tbd">TBD</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''


def render_completed_matches(playoff_matches: List[Dict], team_logo_files: Dict[str, str]) -> str:
    """Render completed matches grouped by date."""
    completed_by_date = defaultdict(list)
    for match in playoff_matches:
        completed_by_date[match["date"]].append(match)

    html = ""
    for date in sorted(completed_by_date.keys(), reverse=True):
        dt = datetime.strptime(date, "%Y-%m-%d")
        date_str = dt.strftime("%A %d %b")

        html += f'<div class="date-group"><div class="date-header">{date_str}</div>'

        for match in sorted(completed_by_date[date], key=lambda x: x.get("time", "00:00")):
            home_logo = get_logo_img(match["home"], "match", team_logo_files)
            away_logo = get_logo_img(match["away"], "match", team_logo_files)
            home_winner = "winner" if match.get("winner") == match["home"] else ""
            away_winner = "winner" if match.get("winner") == match["away"] else ""
            time_str = match.get("time", "")
            penalties = f' <span class="penalties">(Pens: {match["penalties"]["home"]}-{match["penalties"]["away"]})</span>' if "penalties" in match else ""

            html += f'''
            <div class="match-row">
                <div class="match-time">{time_str}</div>
                <div class="match-content-wrapper">
                    <div class="match-content">
                        <div class="match-team home {home_winner}">
                            <span class="team-name">{match["home"]}</span>
                            {home_logo}
                        </div>
                        <div class="match-score-box">
                            <span class="score {home_winner}">{match["home_score"]}</span>
                            <span class="score-separator">-</span>
                            <span class="score {away_winner}">{match["away_score"]}</span>
                        </div>
                        <div class="match-team away {away_winner}">
                            {away_logo}
                            <span class="team-name">{match["away"]}</span>
                        </div>
                    </div>
                </div>
                <div class="match-meta">
                    <span class="round-tag">{match["round"]}</span>{penalties}
                </div>
            </div>
            '''
        html += '</div>'

    return f'''
    <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
            <h2>Completed Playoff Matches</h2>
        </div>
        <div class="card-body">
            {html}
        </div>
    </div>
    '''


def render_upcoming_matches(upcoming_matches: List[Dict], team_logo_files: Dict[str, str]) -> str:
    """Render upcoming matches with betting buttons."""
    upcoming_by_date = defaultdict(list)
    for match in upcoming_matches:
        upcoming_by_date[match["date"]].append(match)

    html = ""
    for date in sorted(upcoming_by_date.keys()):
        dt = datetime.strptime(date, "%Y-%m-%d")
        date_str = dt.strftime("%A %d %b")

        html += f'<div class="date-group"><div class="date-header upcoming">{date_str}</div>'

        for match in sorted(upcoming_by_date[date], key=lambda x: x.get("time", "00:00")):
            home_logo = get_logo_img(match["home"], "match", team_logo_files)
            away_logo = get_logo_img(match["away"], "match", team_logo_files)
            time_str = match.get("time", "")
            home_odds = match["odds"].get(match["home"], 0)
            away_odds = match["odds"].get(match["away"], 0)

            html += f'''
            <div class="match-row upcoming" id="match-{match["match_id"]}">
                <div class="match-time">{time_str}</div>
                <div class="match-content-wrapper">
                    <div class="match-content betting">
                        <button class="bet-team-btn home" onclick="selectBet({match["match_id"]}, '{match["home"]}', {home_odds})">
                            <span class="team-name">{match["home"]}</span>
                            {home_logo}
                            <span class="odds-badge">{home_odds}</span>
                        </button>
                        <div class="vs-badge">VS</div>
                        <button class="bet-team-btn away" onclick="selectBet({match["match_id"]}, '{match["away"]}', {away_odds})">
                            <span class="odds-badge">{away_odds}</span>
                            {away_logo}
                            <span class="team-name">{match["away"]}</span>
                        </button>
                    </div>
                </div>
                <div class="match-meta">
                    <span class="round-tag upcoming">{match["round"]}</span>
                </div>
            </div>
            '''
        html += '</div>'

    return f'''
    <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
            <h2>Upcoming Matches - Place Your Bets</h2>
        </div>
        <div class="card-body">
            {html}
        </div>
    </div>
    '''


def render_bets_sidebar(placed_bets: List[Dict]) -> str:
    """Render the placed bets list."""
    if not placed_bets:
        return "<p class='no-bets'>No bets placed yet. Click on team odds below to place a bet!</p>"

    html = ""
    for bet in placed_bets:
        status_class = bet["status"]
        html += f'''
        <div class="bet-card {status_class}">
            <div class="bet-match">{bet["match_description"]}</div>
            <div class="bet-details">
                <strong>{bet["team_to_win"]}</strong> @ {bet["odds"]}x
            </div>
            <div class="bet-amount">
                {bet["amount"]} GC &rarr; {bet["potential_winnings"]} GC
            </div>
            <div class="bet-status">{bet.get("result", bet["status"].upper())}</div>
        </div>
        '''
    return html


def render_bet_form() -> str:
    """Render the bet input form."""
    return '''
    <div class="bet-form" id="bet-form">
        <p id="bet-selection">Select a team to bet on</p>
        <div class="bet-form-row">
            <input type="number" id="bet-amount" placeholder="Amount (GC)" min="1">
            <button class="btn-primary" onclick="placeBet()">Bet</button>
            <button class="btn-secondary" onclick="cancelBet()">Cancel</button>
        </div>
    </div>
    '''


def render_modal() -> str:
    """Render the results modal structure."""
    return '''
    <div class="modal" id="results-modal">
        <div class="modal-content" id="modal-content">
        </div>
    </div>
    '''


def render_scripts() -> str:
    """Render the JavaScript for the betting page."""
    return '''
    <script>
        let selectedMatch = null;
        let selectedTeam = null;
        let selectedOdds = null;

        function selectBet(matchId, team, odds) {
            selectedMatch = matchId;
            selectedTeam = team;
            selectedOdds = odds;
            document.getElementById('bet-selection').innerHTML =
                `<strong>${team}</strong> @ ${odds}x`;
            document.getElementById('bet-form').classList.add('active');
            document.getElementById('bet-amount').focus();
        }

        function cancelBet() {
            selectedMatch = null;
            selectedTeam = null;
            selectedOdds = null;
            document.getElementById('bet-form').classList.remove('active');
        }

        function placeBet() {
            const amount = parseFloat(document.getElementById('bet-amount').value);
            if (!amount || amount <= 0) {
                alert('Please enter a valid bet amount');
                return;
            }

            fetch(window.location.origin + '/api/place_bet', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    match_id: selectedMatch,
                    team_to_win: selectedTeam,
                    amount: amount
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message + '\\nPotential winnings: ' + data.bet.potential_winnings + ' GC');
                    location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            });
        }

        function revealResults() {
            if (!confirm('Are you sure you want to reveal the results? This cannot be undone!')) return;

            fetch(window.location.origin + '/api/reveal_results')
            .then(r => r.json())
            .then(data => {
                let html = '<h2>Results Revealed</h2>';

                // Match results
                data.match_results.forEach(m => {
                    html += `<div class="result-item">
                        <div class="match">${m.match}</div>
                        <div class="details">${m.round} &bull; ${m.score} &bull; Winner: <strong style="color:#10b981">${m.winner}</strong></div>
                    </div>`;
                });

                // Bet results
                if (data.bets.length > 0) {
                    html += '<h3 style="font-size:14px;color:#888;margin:20px 0 12px;">Your Bets</h3>';
                    data.bets.forEach(b => {
                        const statusClass = b.status === 'won' ? 'won' : 'lost';
                        html += `<div class="result-item ${statusClass}">
                            <div class="match">${b.match_description}</div>
                            <div class="details">${b.team_to_win} @ ${b.odds}x for ${b.amount} GC &rarr; <strong>${b.result}</strong></div>
                        </div>`;
                    });
                }

                // Final balance
                const profit = data.final_balance - 1000;
                const profitClass = profit >= 0 ? 'positive' : 'negative';
                const profitStr = profit >= 0 ? '+' + profit.toFixed(2) : profit.toFixed(2);
                html += `<div class="final-result">
                    <div class="balance">${data.final_balance.toFixed(2)} GC</div>
                    <div class="profit ${profitClass}">${profitStr} GC from start</div>
                </div>`;

                html += '<button class="modal-close" onclick="closeModal()">Close</button>';

                document.getElementById('modal-content').innerHTML = html;
                document.getElementById('results-modal').classList.add('active');
            });
        }

        function closeModal() {
            document.getElementById('results-modal').classList.remove('active');
            location.reload();
        }
    </script>
    '''


def render_page(body_content: str) -> str:
    """Render the full HTML page with CSS imports.

    CSS paths are relative and will work in both local and Colab iframe environments
    because the server handles them at the correct origin.
    """
    css_links = "\n        ".join([f'<link rel="stylesheet" href="/css/{css}">' for css in CSS_FILES])

    return f'''<!DOCTYPE html>
<html>
<head>
    <title>GalacticBets.io - Intergalactic Sports Betting</title>
    <meta charset="UTF-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    {css_links}
</head>
<body>
    {body_content}
    {render_scripts()}
</body>
</html>
'''
