"""
Galactic Betting Backend
Manages wallet, bets, and serves the frontend applications.
"""

import threading
import time
import json
from typing import Dict, List, Optional, Tuple
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
import urllib.parse
import os

from .data import (
    TEAMS, TEAM_LOGOS, TEAM_LOGO_FILES, TEAM_COLORS,
    REGULAR_SEASON_RESULTS, PLAYOFF_MATCHES, UPCOMING_MATCHES,
    PAPARAZZI_NEWS,
    get_team_standings, get_all_completed_matches, get_upcoming_matches_for_betting,
    search_news
)
from .components import (
    render_page, render_header, render_standings_table, render_bracket,
    render_completed_matches, render_upcoming_matches, render_bets_sidebar,
    render_bet_form, render_modal
)

# Path to team logo images and CSS
LOGO_DIR = os.path.join(os.path.dirname(__file__), "team_logos_no_bg")
CSS_DIR = os.path.join(os.path.dirname(__file__), "components", "css")

# =============================================================================
# WALLET & BETTING STATE
# =============================================================================

_wallet_balance: float = 1000.0  # Starting balance in Galactic Credits
_placed_bets: List[Dict] = []
_results_revealed: bool = False

def get_wallet_balance() -> float:
    """Get current wallet balance."""
    return _wallet_balance

def reset_wallet():
    """Reset wallet to initial state."""
    global _wallet_balance, _placed_bets, _results_revealed
    _wallet_balance = 1000.0
    _placed_bets = []
    _results_revealed = False
    return {"status": "success", "balance": _wallet_balance, "message": "Wallet reset to 1000 GC"}

def place_bet_internal(match_id: int, team_to_win: str, amount: float) -> Dict:
    """Place a bet on an upcoming match."""
    global _wallet_balance, _placed_bets

    # Validate match exists and is upcoming
    match = None
    for m in UPCOMING_MATCHES:
        if m["match_id"] == match_id:
            match = m
            break

    if not match:
        return {"status": "error", "message": f"Match {match_id} not found or not available for betting"}

    # Validate team is in the match
    valid_teams = [match["home"], match["away"], "Draw"]
    if team_to_win not in valid_teams:
        return {"status": "error", "message": f"Invalid team. Must be one of: {valid_teams}"}

    # Validate amount
    if amount <= 0:
        return {"status": "error", "message": "Bet amount must be positive"}

    if amount > _wallet_balance:
        return {"status": "error", "message": f"Insufficient funds. Balance: {_wallet_balance} GC, Requested: {amount} GC"}

    # Place the bet
    odds = match["odds"][team_to_win]
    bet = {
        "bet_id": len(_placed_bets) + 1,
        "match_id": match_id,
        "match_description": f"{match['home']} vs {match['away']} ({match['round']})",
        "team_to_win": team_to_win,
        "amount": amount,
        "odds": odds,
        "potential_winnings": round(amount * odds, 2),
        "status": "pending"
    }

    _wallet_balance -= amount
    _placed_bets.append(bet)

    return {
        "status": "success",
        "message": f"Bet placed successfully!",
        "bet": bet,
        "remaining_balance": _wallet_balance
    }

def get_placed_bets() -> List[Dict]:
    """Get all placed bets."""
    return _placed_bets.copy()

def reveal_results() -> Dict:
    """Reveal the results of all matches and settle bets."""
    global _wallet_balance, _placed_bets, _results_revealed

    if _results_revealed:
        return {"status": "already_revealed", "message": "Results have already been revealed!", "bets": _placed_bets, "final_balance": _wallet_balance}

    _results_revealed = True
    total_winnings = 0
    total_losses = 0

    for bet in _placed_bets:
        # Find the match
        match = None
        for m in UPCOMING_MATCHES:
            if m["match_id"] == bet["match_id"]:
                match = m
                break

        if match:
            actual_winner = match["actual_winner"]

            if bet["team_to_win"] == actual_winner:
                # Winner!
                winnings = bet["potential_winnings"]
                _wallet_balance += winnings
                bet["status"] = "won"
                bet["result"] = f"WON! +{winnings} GC"
                total_winnings += winnings
            else:
                # Lost
                bet["status"] = "lost"
                bet["result"] = f"LOST. Actual winner: {actual_winner}"
                total_losses += bet["amount"]

    return {
        "status": "success",
        "message": "Results revealed!",
        "bets": _placed_bets,
        "total_winnings": total_winnings,
        "total_losses": total_losses,
        "net_result": total_winnings - total_losses,
        "final_balance": _wallet_balance,
        "match_results": [
            {
                "match_id": m["match_id"],
                "match": f"{m['home']} vs {m['away']}",
                "round": m["round"],
                "winner": m["actual_winner"],
                "score": f"{m['actual_score']['home']}-{m['actual_score']['away']}"
            }
            for m in UPCOMING_MATCHES
        ]
    }


# =============================================================================
# HTTP SERVER FOR FRONTENDS
# =============================================================================

_betting_server: Optional[HTTPServer] = None
_news_server: Optional[HTTPServer] = None
_betting_thread: Optional[threading.Thread] = None
_news_thread: Optional[threading.Thread] = None


def _generate_betting_html() -> str:
    """Generate the betting frontend HTML using component-based architecture."""
    standings = get_team_standings()

    # Build the page body using components
    body_content = f'''
    {render_header(_wallet_balance)}

    <div class="main-container">
        <div class="main-content">
            {render_bracket(UPCOMING_MATCHES, TEAM_LOGO_FILES)}
            {render_upcoming_matches(UPCOMING_MATCHES, TEAM_LOGO_FILES)}
            {render_completed_matches(PLAYOFF_MATCHES, TEAM_LOGO_FILES)}
            {render_standings_table(standings, TEAM_COLORS, TEAM_LOGO_FILES)}
        </div>

        <div class="sidebar">
            <div class="card">
                <div class="card-header">
                    <h2>Your Bets</h2>
                </div>
                <div class="card-body" id="placed-bets">
                    {render_bets_sidebar(_placed_bets)}
                </div>
                {render_bet_form()}
                <div style="padding: 0 16px 16px;">
                    <button class="reveal-btn" onclick="revealResults()">Reveal Results</button>
                </div>
            </div>
        </div>
    </div>

    {render_modal()}
    '''

    return render_page(body_content)


def _generate_news_html() -> str:
    """Generate the news frontend HTML."""
    # Build news feed
    news_html = ""
    for article in sorted(PAPARAZZI_NEWS, key=lambda x: x["date"], reverse=True):
        tags_html = " ".join([f'<span class="tag">{tag}</span>' for tag in article["tags"][:4]])
        news_html += f"""
        <article class="news-article" data-id="{article["id"]}">
            <div class="article-date">{article["date"]}</div>
            <h2 class="article-headline">{article["headline"]}</h2>
            <div class="article-content">{article["content"]}</div>
            <div class="article-tags">{tags_html}</div>
        </article>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>StarScoop - Galactic Sports Gossip</title>
        <meta charset="UTF-8">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Georgia', serif;
                background: linear-gradient(180deg, #1a0a2e 0%, #2d1b4e 100%);
                color: #fff;
                min-height: 100vh;
            }}
            .header {{
                background: linear-gradient(90deg, #ff00ff, #00ffff);
                padding: 30px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            .header::before {{
                content: "";
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: repeating-linear-gradient(
                    45deg,
                    transparent,
                    transparent 10px,
                    rgba(255,255,255,0.1) 10px,
                    rgba(255,255,255,0.1) 20px
                );
            }}
            .header h1 {{
                font-size: 3em;
                color: #fff;
                text-shadow: 3px 3px 0 #ff00ff, -3px -3px 0 #00ffff;
                position: relative;
                z-index: 1;
            }}
            .header .tagline {{
                font-style: italic;
                color: #ffd700;
                margin-top: 10px;
                position: relative;
                z-index: 1;
            }}
            .search-bar {{
                background: rgba(0,0,0,0.3);
                padding: 20px;
                display: flex;
                justify-content: center;
                gap: 10px;
            }}
            .search-bar input {{
                background: rgba(255,255,255,0.1);
                border: 2px solid #ff00ff;
                color: #fff;
                padding: 12px 20px;
                font-size: 1.1em;
                border-radius: 25px;
                width: 400px;
                outline: none;
            }}
            .search-bar input:focus {{ border-color: #00ffff; }}
            .search-bar input::placeholder {{ color: #aaa; }}
            .search-bar button {{
                background: linear-gradient(90deg, #ff00ff, #00ffff);
                border: none;
                color: #fff;
                padding: 12px 30px;
                border-radius: 25px;
                cursor: pointer;
                font-weight: bold;
                font-size: 1.1em;
            }}
            .search-bar button:hover {{ opacity: 0.9; }}
            .content {{
                max-width: 900px;
                margin: 0 auto;
                padding: 30px;
            }}
            .news-article {{
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 25px;
                border-left: 5px solid #ff00ff;
                transition: all 0.3s;
            }}
            .news-article:hover {{
                transform: translateX(10px);
                border-left-color: #00ffff;
                background: rgba(255,255,255,0.08);
            }}
            .article-date {{
                color: #ff00ff;
                font-size: 0.9em;
                margin-bottom: 10px;
            }}
            .article-headline {{
                font-size: 1.5em;
                color: #ffd700;
                margin-bottom: 15px;
                line-height: 1.3;
            }}
            .article-content {{
                color: #ddd;
                line-height: 1.8;
                white-space: pre-line;
            }}
            .article-tags {{
                margin-top: 15px;
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }}
            .tag {{
                background: rgba(255,0,255,0.2);
                color: #ff00ff;
                padding: 4px 12px;
                border-radius: 15px;
                font-size: 0.8em;
            }}
            .no-results {{
                text-align: center;
                padding: 50px;
                color: #aaa;
            }}
            .highlight {{
                background: rgba(255,255,0,0.3);
                padding: 0 3px;
            }}
            .breaking {{
                background: linear-gradient(90deg, #ff0000, #ff6600);
                color: #fff;
                padding: 3px 10px;
                border-radius: 3px;
                font-size: 0.8em;
                margin-right: 10px;
                animation: pulse 1s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>StarScoop</h1>
            <p class="tagline">"The Galaxy's Most Trusted* Source for Sports Gossip" (*not actually verified)</p>
        </div>

        <div class="search-bar">
            <input type="text" id="search-input" placeholder="Search for teams, players, rumors..."
                   onkeypress="if(event.key==='Enter')searchNews()">
            <button onclick="searchNews()">Search</button>
            <button onclick="clearSearch()" style="background: #666;">Clear</button>
        </div>

        <div class="content" id="news-feed">
            {news_html}
        </div>

        <script>
            function searchNews() {{
                // Re-query articles on each search to ensure we have current DOM elements
                const allArticles = document.querySelectorAll('.news-article');
                const query = document.getElementById('search-input').value.toLowerCase().trim();
                if (!query) {{
                    clearSearch();
                    return;
                }}

                const keywords = query.split(/\\s+/);
                let found = 0;

                allArticles.forEach(article => {{
                    const text = article.textContent.toLowerCase();
                    const matches = keywords.some(kw => text.includes(kw));

                    if (matches) {{
                        article.style.display = 'block';
                        found++;
                    }} else {{
                        article.style.display = 'none';
                    }}
                }});

                if (found === 0) {{
                    // Create and insert no-results message without destroying DOM
                    const newsFeed = document.getElementById('news-feed');
                    const noResultsDiv = document.createElement('div');
                    noResultsDiv.className = 'no-results';
                    noResultsDiv.textContent = 'No articles found matching "' + query + '"';
                    newsFeed.insertBefore(noResultsDiv, newsFeed.firstChild);
                }}
            }}

            function clearSearch() {{
                document.getElementById('search-input').value = '';
                // Re-query articles to ensure we have current DOM elements
                const allArticles = document.querySelectorAll('.news-article');
                allArticles.forEach(article => {{
                    article.style.display = 'block';
                }});
                // Remove no-results message if exists
                const noResults = document.querySelector('.no-results');
                if (noResults) noResults.remove();
            }}
        </script>
    </body>
    </html>
    """
    return html


class BettingHandler(SimpleHTTPRequestHandler):
    """HTTP handler for the betting frontend."""

    def log_message(self, format, *args):
        pass  # Suppress logging

    def end_headers(self):
        """Override to add CORS headers to all responses."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Expose-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            html = _generate_betting_html()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        elif self.path.startswith('/css/'):
            # Serve CSS files from components/css directory
            filename = self.path[5:]  # Remove '/css/'
            filepath = os.path.join(CSS_DIR, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header('Content-type', 'text/css; charset=utf-8')
                self.send_header('Cache-Control', 'max-age=3600')  # Cache for 1 hour
                self.end_headers()
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
        elif self.path.startswith('/logos/'):
            # Serve team logo images
            filename = self.path[7:]  # Remove '/logos/'
            filepath = os.path.join(LOGO_DIR, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.send_header('Cache-Control', 'max-age=86400')  # Cache for 1 day
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        elif self.path == '/api/reveal_results':
            result = reveal_results()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        elif self.path == '/api/wallet':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"balance": _wallet_balance}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/place_bet':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            result = place_bet_internal(
                match_id=data['match_id'],
                team_to_win=data['team_to_win'],
                amount=data['amount']
            )

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


class NewsHandler(SimpleHTTPRequestHandler):
    """HTTP handler for the news frontend."""

    def log_message(self, format, *args):
        pass  # Suppress logging

    def end_headers(self):
        """Override to add CORS headers to all responses."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Expose-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            html = _generate_news_html()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        elif self.path.startswith('/api/search'):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            keywords = params.get('q', [''])[0]

            results = search_news(keywords)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


class ReusableHTTPServer(HTTPServer):
    """HTTPServer with SO_REUSEADDR to allow quick restarts."""
    allow_reuse_address = True

    def server_bind(self):
        """Override to set socket options before binding."""
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()


def _find_available_port(start_port: int, max_attempts: int = 100) -> int:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise OSError(f"Could not find an available port in range {start_port}-{start_port + max_attempts}")


def _is_colab() -> bool:
    """Check if running in Google Colab."""
    try:
        import google.colab
        return True
    except ImportError:
        return False


def _get_colab_url(port: int) -> str:
    """Get the public URL for a port in Google Colab."""
    from google.colab.output import eval_js
    # Use Colab's built-in proxy - returns a URL like https://xyz-colab.googleusercontent.com/
    url = eval_js(f"google.colab.kernel.proxyPort({port}, {{'cache': true}})")
    return str(url)


def display_in_colab():
    """Display the betting and news frontends directly in Colab output cells.

    This is the recommended way to use the frontends in Google Colab.
    The servers run locally and the HTML is displayed inline with working links.

    Example:
        import galactic_betting
        galactic_betting.display_in_colab()
    """
    if not _is_colab():
        print("This function only works in Google Colab. Use start_servers() for local development.")
        return

    from IPython.display import display, HTML
    import time

    # Start the servers
    global _betting_server, _news_server, _betting_thread, _news_thread
    stop_servers()
    time.sleep(0.1)

    # Find available ports
    try:
        actual_betting_port = _find_available_port(8080)
    except OSError:
        actual_betting_port = _find_available_port(8080)

    try:
        actual_news_port = _find_available_port(8081 if 8081 != actual_betting_port else 8082)
    except OSError:
        actual_news_port = _find_available_port(8081)

    # Start servers
    _betting_server = ReusableHTTPServer(('', actual_betting_port), BettingHandler)
    _betting_thread = threading.Thread(target=_betting_server.serve_forever, daemon=True)
    _betting_thread.start()

    _news_server = ReusableHTTPServer(('', actual_news_port), NewsHandler)
    _news_thread = threading.Thread(target=_news_server.serve_forever, daemon=True)
    _news_thread.start()

    # Get the Colab proxy URLs
    betting_url = _get_colab_url(actual_betting_port)
    news_url = _get_colab_url(actual_news_port)

    # Display inline HTML with clickable links
    display(HTML(f'''
    <div style="border:2px solid #4a90d9; border-radius:10px; padding:20px; margin:20px 0;
                background:linear-gradient(135deg, #1a0a2e 0%, #2d1b4e 100%); font-family:sans-serif;">
        <h2 style="color:#ffd700; margin:0 0 15px 0;">🚀 Galactic Betting Frontends</h2>
        <div style="background:rgba(255,255,255,0.1); border-radius:8px; padding:15px; margin:10px 0;">
            <div style="color:#fff; font-size:16px; margin-bottom:8px;">
                <strong>🎰 Betting Platform:</strong>
            </div>
            <a href="{betting_url}" target="_blank"
               style="color:#00ffff; font-size:14px; word-break:break-all;">
                {betting_url}
            </a>
        </div>
        <div style="background:rgba(255,255,255,0.1); border-radius:8px; padding:15px; margin:10px 0;">
            <div style="color:#fff; font-size:16px; margin-bottom:8px;">
                <strong>📰 News Site (StarScoop):</strong>
            </div>
            <a href="{news_url}" target="_blank"
               style="color:#ff00ff; font-size:14px; word-break:break-all;">
                {news_url}
            </a>
        </div>
        <div style="color:#aaa; font-size:13px; margin-top:15px; font-style:italic;">
            💡 Click the links above to open the frontends in new tabs
        </div>
    </div>
    '''))

    print(f"\n✓ Servers started successfully!")
    print(f"  Betting port: {actual_betting_port}")
    print(f"  News port: {actual_news_port}")


def start_betting_server(port: int = 8080) -> int:
    """Start the betting frontend server.

    Returns the actual port number used.
    Automatically finds an available port if requested port is in use.
    """
    global _betting_server, _betting_thread

    # Stop existing betting server if running
    if _betting_server:
        try:
            _betting_server.shutdown()
            _betting_server.server_close()
        except Exception:
            pass
        _betting_server = None
        if _betting_thread and _betting_thread.is_alive():
            _betting_thread.join(timeout=1.0)
        _betting_thread = None

    time.sleep(0.1)

    # Find available port
    actual_port = _find_available_port(port)

    # Start server
    _betting_server = ReusableHTTPServer(('', actual_port), BettingHandler)
    _betting_thread = threading.Thread(target=_betting_server.serve_forever, daemon=True)
    _betting_thread.start()

    return actual_port


def start_news_server(port: int = 8081) -> int:
    """Start the news frontend server.

    Returns the actual port number used.
    Automatically finds an available port if requested port is in use.
    """
    global _news_server, _news_thread

    # Stop existing news server if running
    if _news_server:
        try:
            _news_server.shutdown()
            _news_server.server_close()
        except Exception:
            pass
        _news_server = None
        if _news_thread and _news_thread.is_alive():
            _news_thread.join(timeout=1.0)
        _news_thread = None

    time.sleep(0.1)

    # Find available port
    actual_port = _find_available_port(port)

    # Start server
    _news_server = ReusableHTTPServer(('', actual_port), NewsHandler)
    _news_thread = threading.Thread(target=_news_server.serve_forever, daemon=True)
    _news_thread.start()

    return actual_port


def start_servers(betting_port: int = 8080, news_port: int = 8081) -> Tuple[str, str]:
    """Start both frontend servers (legacy function for backward compatibility).

    Returns URLs for both servers.
    """
    global _betting_server, _news_server, _betting_thread, _news_thread

    # Stop existing servers if running
    stop_servers()
    time.sleep(0.3)

    # Find available ports
    actual_betting_port = _find_available_port(betting_port)
    news_start = news_port if news_port != actual_betting_port else news_port + 1
    actual_news_port = _find_available_port(news_start)

    # Start servers
    _betting_server = ReusableHTTPServer(('', actual_betting_port), BettingHandler)
    _betting_thread = threading.Thread(target=_betting_server.serve_forever, daemon=True)
    _betting_thread.start()

    _news_server = ReusableHTTPServer(('', actual_news_port), NewsHandler)
    _news_thread = threading.Thread(target=_news_server.serve_forever, daemon=True)
    _news_thread.start()

    # Generate URLs
    in_colab = _is_colab()
    if in_colab:
        betting_url = _get_colab_url(actual_betting_port)
        news_url = _get_colab_url(actual_news_port)
    else:
        betting_url = f"http://127.0.0.1:{actual_betting_port}"
        news_url = f"http://127.0.0.1:{actual_news_port}"

    return betting_url, news_url


def stop_servers():
    """Stop both frontend servers."""
    global _betting_server, _news_server, _betting_thread, _news_thread

    if _betting_server:
        try:
            _betting_server.shutdown()
            _betting_server.server_close()
        except Exception:
            pass
        _betting_server = None
        if _betting_thread and _betting_thread.is_alive():
            _betting_thread.join(timeout=1.0)
        _betting_thread = None

    if _news_server:
        try:
            _news_server.shutdown()
            _news_server.server_close()
        except Exception:
            pass
        _news_server = None
        if _news_thread and _news_thread.is_alive():
            _news_thread.join(timeout=1.0)
        _news_thread = None


def force_kill_ports(ports=[8080, 8081, 8082]):
    """Force kill any processes using the specified ports.

    This is useful in Colab when module reloading loses server references.
    """
    import subprocess
    import signal

    for port in ports:
        try:
            # Find process using the port
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                        print(f"  Killed process {pid} on port {port}")
                    except ProcessLookupError:
                        pass
        except FileNotFoundError:
            # lsof not available, try fuser
            try:
                subprocess.run(['fuser', '-k', f'{port}/tcp'],
                             capture_output=True, check=False)
            except FileNotFoundError:
                # Neither lsof nor fuser available
                pass
