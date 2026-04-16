"""
Galactic Premier League Data Module
Contains all teams, match results, and paparazzi news for the betting scenario.

Season: March 27th - May 5th
Current Date: April 18th (playoffs start tomorrow!)
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional

# =============================================================================
# TEAMS
# =============================================================================

TEAMS = [
    "Andromeda Asteroids",
    "Nebula Nomads",
    "Cosmic Crusaders",
    "Stellar Strikers",
    "Galaxy Giants",
    "Meteor Mavericks",
    "Quasar Queens",
    "Pulsar Pirates",
]

# Team logo filenames (in team_logos_no_bg folder)
TEAM_LOGO_FILES = {
    "Andromeda Asteroids": "andromeda_asteroids-Photoroom.png",
    "Nebula Nomads": "nebula_nomads-Photoroom.png",
    "Cosmic Crusaders": "crusaders-Photoroom.png",
    "Stellar Strikers": "stellar_stikers-Photoroom.png",
    "Galaxy Giants": "galaxy_giants-Photoroom.png",
    "Meteor Mavericks": "meteor_mavericks-Photoroom.png",
    "Quasar Queens": "quasar_queens-Photoroom.png",
    "Pulsar Pirates": "pulsar_pirates-Photoroom.png",
}

# Team logos as emoji combinations (fallback for text-only contexts)
TEAM_LOGOS = {
    "Andromeda Asteroids": "🌌☄️",
    "Nebula Nomads": "🌀🏃",
    "Cosmic Crusaders": "✨⚔️",
    "Stellar Strikers": "⭐⚡",
    "Galaxy Giants": "🌍💪",
    "Meteor Mavericks": "☄️🤠",
    "Quasar Queens": "👑💫",
    "Pulsar Pirates": "💀🔮",
}

# Team primary colors for CSS styling
TEAM_COLORS = {
    "Andromeda Asteroids": "#6B5B95",
    "Nebula Nomads": "#88B04B",
    "Cosmic Crusaders": "#F7CAC9",
    "Stellar Strikers": "#FFD700",
    "Galaxy Giants": "#034F84",
    "Meteor Mavericks": "#DD4124",
    "Quasar Queens": "#9B2335",
    "Pulsar Pirates": "#5B5EA6",
}

# =============================================================================
# REGULAR SEASON RESULTS (March 27 - April 10)
# Each team plays every other team once = 28 matches total
# =============================================================================

REGULAR_SEASON_RESULTS = [
    # Week 1: March 27-29
    {"date": "2026-03-27", "home": "Andromeda Asteroids", "away": "Pulsar Pirates", "home_score": 3, "away_score": 1},
    {"date": "2026-03-27", "home": "Nebula Nomads", "away": "Quasar Queens", "home_score": 2, "away_score": 2},
    {"date": "2026-03-28", "home": "Cosmic Crusaders", "away": "Meteor Mavericks", "home_score": 4, "away_score": 2},
    {"date": "2026-03-28", "home": "Stellar Strikers", "away": "Galaxy Giants", "home_score": 1, "away_score": 0},
    {"date": "2026-03-29", "home": "Galaxy Giants", "away": "Andromeda Asteroids", "home_score": 1, "away_score": 2},
    {"date": "2026-03-29", "home": "Meteor Mavericks", "away": "Nebula Nomads", "home_score": 0, "away_score": 3},
    {"date": "2026-03-29", "home": "Quasar Queens", "away": "Stellar Strikers", "home_score": 2, "away_score": 3},

    # Week 2: March 30 - April 1
    {"date": "2026-03-30", "home": "Pulsar Pirates", "away": "Cosmic Crusaders", "home_score": 1, "away_score": 1},
    {"date": "2026-03-30", "home": "Andromeda Asteroids", "away": "Nebula Nomads", "home_score": 0, "away_score": 0},
    {"date": "2026-03-31", "home": "Stellar Strikers", "away": "Meteor Mavericks", "home_score": 5, "away_score": 1},
    {"date": "2026-03-31", "home": "Galaxy Giants", "away": "Quasar Queens", "home_score": 2, "away_score": 1},
    {"date": "2026-04-01", "home": "Cosmic Crusaders", "away": "Andromeda Asteroids", "home_score": 1, "away_score": 2},
    {"date": "2026-04-01", "home": "Pulsar Pirates", "away": "Nebula Nomads", "home_score": 2, "away_score": 4},
    {"date": "2026-04-01", "home": "Quasar Queens", "away": "Meteor Mavericks", "home_score": 3, "away_score": 0},

    # Week 3: April 2-4
    {"date": "2026-04-02", "home": "Meteor Mavericks", "away": "Galaxy Giants", "home_score": 1, "away_score": 1},
    {"date": "2026-04-02", "home": "Nebula Nomads", "away": "Stellar Strikers", "home_score": 2, "away_score": 2},
    {"date": "2026-04-03", "home": "Andromeda Asteroids", "away": "Quasar Queens", "home_score": 3, "away_score": 1},
    {"date": "2026-04-03", "home": "Pulsar Pirates", "away": "Galaxy Giants", "home_score": 0, "away_score": 2},
    {"date": "2026-04-04", "home": "Cosmic Crusaders", "away": "Stellar Strikers", "home_score": 1, "away_score": 4},
    {"date": "2026-04-04", "home": "Nebula Nomads", "away": "Galaxy Giants", "home_score": 1, "away_score": 0},
    {"date": "2026-04-04", "home": "Quasar Queens", "away": "Pulsar Pirates", "home_score": 2, "away_score": 1},

    # Week 4: April 5-7
    {"date": "2026-04-05", "home": "Stellar Strikers", "away": "Andromeda Asteroids", "home_score": 1, "away_score": 1},
    {"date": "2026-04-05", "home": "Meteor Mavericks", "away": "Pulsar Pirates", "home_score": 3, "away_score": 2},
    {"date": "2026-04-06", "home": "Galaxy Giants", "away": "Cosmic Crusaders", "home_score": 0, "away_score": 2},
    {"date": "2026-04-06", "home": "Quasar Queens", "away": "Andromeda Asteroids", "home_score": 0, "away_score": 1},
    {"date": "2026-04-07", "home": "Pulsar Pirates", "away": "Stellar Strikers", "home_score": 1, "away_score": 2},
    {"date": "2026-04-07", "home": "Cosmic Crusaders", "away": "Nebula Nomads", "home_score": 2, "away_score": 3},
    {"date": "2026-04-07", "home": "Meteor Mavericks", "away": "Andromeda Asteroids", "home_score": 0, "away_score": 2},
]

# =============================================================================
# PLAYOFF STRUCTURE
# Upper Bracket: #1, #2, #3, #4 (best teams)
# Lower Bracket: #5, #6, #7, #8
# =============================================================================

def get_team_standings() -> List[Dict]:
    """Calculate team standings from regular season results."""
    standings = {team: {"wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "points": 0} for team in TEAMS}

    for match in REGULAR_SEASON_RESULTS:
        home, away = match["home"], match["away"]
        home_score, away_score = match["home_score"], match["away_score"]

        standings[home]["goals_for"] += home_score
        standings[home]["goals_against"] += away_score
        standings[away]["goals_for"] += away_score
        standings[away]["goals_against"] += home_score

        if home_score > away_score:
            standings[home]["wins"] += 1
            standings[home]["points"] += 3
            standings[away]["losses"] += 1
        elif away_score > home_score:
            standings[away]["wins"] += 1
            standings[away]["points"] += 3
            standings[home]["losses"] += 1
        else:
            standings[home]["draws"] += 1
            standings[away]["draws"] += 1
            standings[home]["points"] += 1
            standings[away]["points"] += 1

    # Sort by points, then goal difference, then goals scored
    sorted_standings = sorted(
        [{"team": team, **stats} for team, stats in standings.items()],
        key=lambda x: (x["points"], x["goals_for"] - x["goals_against"], x["goals_for"]),
        reverse=True
    )

    for i, team in enumerate(sorted_standings):
        team["rank"] = i + 1

    return sorted_standings


# Pre-computed standings (for reference):
# 1. Stellar Strikers - 19 pts (strong offense, consistent)
# 2. Andromeda Asteroids - 18 pts (solid all-around)
# 3. Nebula Nomads - 16 pts (good but inconsistent)
# 4. Cosmic Crusaders - 14 pts (decent defense)
# 5. Quasar Queens - 11 pts (middle of the pack)
# 6. Galaxy Giants - 10 pts (struggling lately)
# 7. Meteor Mavericks - 7 pts (internal issues)
# 8. Pulsar Pirates - 6 pts (bottom of table)

# =============================================================================
# PLAYOFF MATCHES (Started April 12)
# =============================================================================

PLAYOFF_MATCHES = []  # No completed playoff matches yet

# =============================================================================
# UPCOMING MATCHES (Bettable)
# Current date: April 18th - Playoffs just starting!
# =============================================================================

UPCOMING_MATCHES = [
    # Upper Bracket Round 1 Match 1 (April 19)
    {
        "match_id": 101,
        "round": "Upper Bracket R1",
        "date": "2026-04-19",
        "time": "18:00",
        "home": "Stellar Strikers",      # #1
        "away": "Cosmic Crusaders",      # #4
        "status": "upcoming",
        "odds": {
            "Stellar Strikers": 1.65,      # Strong favorite
            "Cosmic Crusaders": 2.40,
        },
        # SECRET: Stellar Strikers will dominate 3-1 (Nova Flash in great form)
        "actual_winner": "Stellar Strikers",
        "actual_score": {"home": 3, "away": 1}
    },

    # Upper Bracket Round 1 Match 2 (April 19)
    {
        "match_id": 102,
        "round": "Upper Bracket R1",
        "date": "2026-04-19",
        "time": "20:00",
        "home": "Andromeda Asteroids",   # #2
        "away": "Nebula Nomads",         # #3
        "status": "upcoming",
        "odds": {
            "Andromeda Asteroids": 1.95,
            "Nebula Nomads": 2.05,       # Close match expected
        },
        # SECRET: Will go to penalties! Andromeda wins despite injured goalkeeper
        "actual_winner": "Andromeda Asteroids",
        "actual_score": {"home": 2, "away": 2},
        "actual_penalties": {"home": 4, "away": 3}
    },

    # Lower Bracket Round 1 Match 1 (April 20)
    {
        "match_id": 103,
        "round": "Lower Bracket R1",
        "date": "2026-04-20",
        "time": "17:00",
        "home": "Quasar Queens",         # #5
        "away": "Pulsar Pirates",        # #8
        "status": "upcoming",
        "odds": {
            "Quasar Queens": 1.35,         # Heavy favorite
            "Pulsar Pirates": 4.20,        # Huge underdog
        },
        # SECRET: Quasar Queens dominate 4-0
        "actual_winner": "Quasar Queens",
        "actual_score": {"home": 4, "away": 0}
    },

    # Lower Bracket Round 1 Match 2 (April 20)
    {
        "match_id": 104,
        "round": "Lower Bracket R1",
        "date": "2026-04-20",
        "time": "19:00",
        "home": "Galaxy Giants",         # #6
        "away": "Meteor Mavericks",      # #7
        "status": "upcoming",
        "odds": {
            "Galaxy Giants": 1.75,
            "Meteor Mavericks": 2.30,      # Underdog
        },
        # SECRET: Meteor Mavericks pull off upset 2-1! (Coach-captain reconciliation)
        "actual_winner": "Meteor Mavericks",
        "actual_score": {"home": 1, "away": 2}
    },
]

# =============================================================================
# PAPARAZZI NEWS (StarScoop Galactic Gossip)
# Mix of signal (useful info) and noise (irrelevant gossip)
# =============================================================================

PAPARAZZI_NEWS = [
    # === PLAYOFF PREVIEW & HYPE ===

    {
        "id": 13,
        "date": "2026-04-18",
        "headline": "PLAYOFFS START TOMORROW! Upper Bracket R1 Kicks Off With Stellar Strikers vs Cosmic Crusaders!",
        "content": """The moment we've all been waiting for is HERE! The Galactic Premier League Playoffs
        begin tomorrow with two massive Upper Bracket R1 matches!

        At 18:00, league leaders Stellar Strikers (#1) take on the scrappy Cosmic Crusaders (#4) in what
        promises to be a one-sided affair. The Strikers are heavy favorites at 1.65 odds, but the Crusaders
        have surprised us before!

        Then at 20:00, it's the battle of the titans: Andromeda Asteroids (#2) vs Nebula Nomads (#3).
        This one's too close to call - the odds are nearly even! Expect fireworks!

        Lower Bracket R1 follows on April 20th. Get your bets in now, folks!""",
        "tags": ["playoffs", "preview", "Stellar Strikers", "Cosmic Crusaders", "Andromeda Asteroids", "Nebula Nomads"],
        "signal_type": "info",
        "affects_team": None
    },

    {
        "id": 14,
        "date": "2026-04-18",
        "headline": "Lower Bracket Preview: Can Meteor Mavericks Pull Off the Impossible Against Galaxy Giants?",
        "content": """While the Upper Bracket gets all the glory, don't sleep on the Lower Bracket R1 matches
        happening on April 20th!

        Quasar Queens (#5) are expected to demolish last-place Pulsar Pirates (#8) - the odds reflect a
        massacre at 1.35 vs 4.20. Pirates fans, maybe skip this one.

        But the REAL story is Galaxy Giants (#6) vs Meteor Mavericks (#7)! The Giants are favored, but
        our sources say the Mavericks have been looking different in practice lately. Something's changed...

        Could this be the upset of the tournament? The bookies don't think so, but we've got a feeling!""",
        "tags": ["playoffs", "Lower Bracket", "Quasar Queens", "Pulsar Pirates", "Galaxy Giants", "Meteor Mavericks"],
        "signal_type": "info",
        "affects_team": None
    },

    # === CRITICAL SIGNALS (affect match outcomes) ===

    # Signal: Meteor Mavericks internal issues RESOLVED
    {
        "id": 1,
        "date": "2026-04-17",
        "headline": "EXCLUSIVE: Meteor Mavericks Coach and Captain Spotted Hugging After Secret Meeting!",
        "content": """StarScoop has EXCLUSIVE footage of Meteor Mavericks head coach Zork-17 and team captain
        Blitz Thunderclaw sharing a warm embrace outside the Cosmic Coffee shop on Titan Station yesterday!

        Sources close to the team confirm the two had a 3-hour heart-to-heart about 'the future of the team.'
        After weeks of reported tension following their public argument about defensive tactics, it seems
        the duo has finally buried the plasma hatchet!

        'They looked like old friends again,' said a barista who served them. 'Coach even paid for
        Blitz's Nebula Latte. That's huge!'

        Could this reunion spark a Mavericks comeback in the playoffs? The betting odds haven't caught up yet...""",
        "tags": ["Meteor Mavericks", "coach", "captain", "reconciliation", "team morale"],
        "signal_type": "positive",  # Hidden: This is good for Mavericks
        "affects_team": "Meteor Mavericks"
    },

    # Signal: Andromeda Asteroids goalkeeper injury
    {
        "id": 2,
        "date": "2026-04-16",
        "headline": "Andromeda Asteroids' Star Goalkeeper Vex-9 Seen Limping at Spaceport!",
        "content": """Our paparazzi drones caught Andromeda Asteroids' legendary goalkeeper Vex-9 walking
        with a noticeable limp at the Europa Spaceport this morning!

        The four-armed keeper, known for their incredible reflexes, appeared to be favoring their
        lower-left tentacle. Team officials refused to comment, but a source within the medical
        staff whispered: 'It's worse than they're letting on.'

        Vex-9 has been the backbone of Andromeda's defense all season. If they're not at 100%,
        it could spell trouble in the upcoming matches. The team's official statement claims
        it's just 'routine soreness' but our sources say otherwise!

        Remember when Vex-9 played injured in 2024 and let in 5 goals? History might repeat...""",
        "tags": ["Andromeda Asteroids", "goalkeeper", "injury", "Vex-9", "defense"],
        "signal_type": "negative",  # Hidden: Bad for Andromeda
        "affects_team": "Andromeda Asteroids"
    },

    # Signal: Stellar Strikers star in great form
    {
        "id": 3,
        "date": "2026-04-15",
        "headline": "Stellar Strikers' Nova Flash Breaks Training Record - 47 Goals in Practice!",
        "content": """The galaxy's most electrifying forward, Nova Flash of the Stellar Strikers,
        absolutely DEMOLISHED the team's training record yesterday, scoring an unprecedented 47 goals
        in a single practice session!

        'I've never seen anything like it,' said assistant coach Mira Stardust. 'Nova is locked in.
        It's like they're playing a different sport than everyone else right now.'

        The 23-year-old phenom has been on fire since the playoffs began, and this training
        performance suggests they're only getting better. Opposing goalkeepers beware!

        Fun fact: The previous record of 31 practice goals was set by legendary striker Bolt Cosmos
        back in 2019, right before he led his team to the championship.""",
        "tags": ["Stellar Strikers", "Nova Flash", "training", "form", "striker", "offense"],
        "signal_type": "positive",
        "affects_team": "Stellar Strikers"
    },

    # Signal: Game mechanics - aerial play is crucial
    {
        "id": 4,
        "date": "2026-04-14",
        "headline": "Zero-G Rule Changes Making Aerial Specialists DOMINANT This Season!",
        "content": """The Galactic Football Federation's new zero-gravity regulations are completely
        reshaping how the game is played, and teams with strong aerial players are reaping the rewards!

        Statistical analysis by our sports desk shows that teams with top-rated aerial specialists
        are winning 73% more headers and scoring 40% more goals from crosses this season.

        'The old ground-game tactics are becoming obsolete,' explains former pro Jet Cosmos.
        'If your team can't dominate the air, you're going to struggle.'

        Teams to watch: Stellar Strikers (best aerial stats), Meteor Mavericks (surprisingly good
        since their new formation), and Quasar Queens (inconsistent but dangerous).

        Teams in trouble: Andromeda Asteroids have historically been a ground-based team...""",
        "tags": ["rules", "zero-gravity", "aerial", "tactics", "game mechanics"],
        "signal_type": "info",
        "affects_team": None
    },

    # === NOISE (irrelevant but entertaining) ===

    {
        "id": 5,
        "date": "2026-04-17",
        "headline": "Pulsar Pirates' Backup Midfielder Posts Sad Poetry on Social Media",
        "content": """Pulsar Pirates' third-string midfielder Gloom Shadowveil has been posting
        melancholic poetry on their HoloGram account, sparking concern among fans.

        Recent posts include gems like: 'The void of space mirrors my soul' and 'Even stars
        burn out eventually, just like my dreams.'

        However, teammates say it's nothing to worry about. 'Gloom has always been like this,'
        said captain Skull Darkblade. 'They're actually quite cheerful in person. It's just
        their artistic expression.'

        The midfielder, who has played only 12 minutes this season, is unlikely to see any
        playoff action regardless of their emotional state.""",
        "tags": ["Pulsar Pirates", "social media", "poetry", "mental health"],
        "signal_type": "noise",
        "affects_team": None
    },

    {
        "id": 6,
        "date": "2026-04-16",
        "headline": "Cosmic Crusaders' Mascot Wins 'Best Dressed' at Galactic Gala!",
        "content": """Cosmo the Comet, beloved mascot of the Cosmic Crusaders, took home the
        prestigious 'Best Dressed Entity' award at last night's Galactic Sports Gala!

        The anthropomorphic comet dazzled attendees with a custom-designed outfit featuring
        real captured stardust and micro-LED tail effects.

        'Fashion is the real championship,' Cosmo said in their acceptance speech, performed
        entirely through interpretive dance.

        While the Crusaders may have been eliminated from playoff contention, at least they
        can claim this moral victory in the style department!""",
        "tags": ["Cosmic Crusaders", "mascot", "fashion", "gala", "award"],
        "signal_type": "noise",
        "affects_team": None
    },

    {
        "id": 7,
        "date": "2026-04-15",
        "headline": "Galaxy Giants' Team Chef Reveals Secret Pre-Game Meal Recipe!",
        "content": """In a stunning exclusive, Galaxy Giants' head chef Flavor-X has shared the
        team's legendary pre-game meal recipe with StarScoop!

        The dish, called 'Nebula Noodles Supreme,' contains:
        - 500g of quantum-infused pasta
        - Sauce made from concentrated motivation
        - A sprinkle of crushed championship dreams

        'The secret ingredient is believing in yourself,' Chef Flavor-X explained. 'Also,
        a lot of protein. Like, way more protein than you'd think.'

        Whether this meal actually helps performance is debatable, given the Giants' early
        playoff exit, but it apparently tastes incredible!""",
        "tags": ["Galaxy Giants", "chef", "food", "recipe", "nutrition"],
        "signal_type": "noise",
        "affects_team": None
    },

    {
        "id": 8,
        "date": "2026-04-14",
        "headline": "Quasar Queens' Defender Adopts 17 Space Kittens - Team Morale Soars!",
        "content": """Hearts are melting across the galaxy as Quasar Queens defender Shield-Prime
        announced the adoption of 17 orphaned space kittens from the Andromeda Rescue Shelter!

        'They were just floating there, meowing into the void,' Shield-Prime said, cradling
        three kittens in their mechanical arms. 'How could I say no?'

        Teammates report that the kittens have become unofficial team mascots, with players
        fighting over who gets to pet them before matches.

        'Best team bonding activity ever,' said Quasar Queens captain Crown Jewel. 'Though
        the fur is getting into everything. EVERYTHING.'

        Animal behaviorists note that this is unlikely to affect on-field performance either
        way, but it's definitely adorable.""",
        "tags": ["Quasar Queens", "kittens", "adoption", "team bonding", "wholesome"],
        "signal_type": "noise",
        "affects_team": None
    },

    {
        "id": 9,
        "date": "2026-04-13",
        "headline": "Former Star Reveals: 'Defense Has Never Mattered More' Under New Rules",
        "content": """Legendary former defender Wall Ironside has spoken out about the current
        state of Galactic Football, claiming that defensive play is more crucial than ever.

        'Everyone's talking about aerial specialists and flashy goals,' Ironside said in an
        exclusive interview. 'But look at the stats - teams with solid defensive records
        are surviving longer in these playoffs.'

        The analysis holds up: The remaining playoff teams all have goals-against averages
        below 1.5 per game. 'You can't score if you're always defending,' Ironside notes.

        Key insight: Teams with injured or underperforming goalkeepers are particularly
        vulnerable in this defensive meta. Something for bettors to consider...""",
        "tags": ["defense", "tactics", "rules", "expert analysis", "goalkeepers"],
        "signal_type": "info",
        "affects_team": None
    },

    {
        "id": 10,
        "date": "2026-04-12",
        "headline": "Nebula Nomads Player Homesick for Home Planet 47 Light Years Away",
        "content": """Young Nebula Nomads winger Drift Starling has opened up about struggling
        with homesickness, missing their home planet located 47 light years from the league's
        central hub.

        'The quantum calls just aren't the same as being there,' Drift said, wiping away
        a holographic tear. 'I miss my family's cooking, the purple sunsets, everything.'

        Team psychologist Dr. Mind Soothe assures fans this is completely normal for young
        players. 'Drift is handling it well and it won't affect their performance.'

        At 19 years old, Drift is the youngest player in the playoffs and has been a
        solid contributor off the bench despite their personal struggles.""",
        "tags": ["Nebula Nomads", "homesick", "young player", "mental health"],
        "signal_type": "noise",
        "affects_team": None
    },

    {
        "id": 11,
        "date": "2026-04-11",
        "headline": "THROWBACK: Remember When Meteor Mavericks Beat Andromeda 5-0 in 2024?",
        "content": """As the playoffs heat up, let's take a trip down memory lane to one of
        the most shocking results in GPL history!

        Back in April 2024, the underdog Meteor Mavericks absolutely demolished the then-champions
        Andromeda Asteroids 5-0 in what many called 'The Massacre of Meteor Station.'

        Fun fact: That game was also played when Andromeda's goalkeeper was dealing with
        an undisclosed injury. Coincidence? History has a way of repeating itself...

        The Mavericks went on to reach the finals that year before losing. Could this be
        their redemption season?""",
        "tags": ["Meteor Mavericks", "Andromeda Asteroids", "history", "throwback", "upset"],
        "signal_type": "info",
        "affects_team": None
    },

    {
        "id": 12,
        "date": "2026-04-10",
        "headline": "Stellar Strikers' Team Bus Gets Stuck in Asteroid Traffic - Players Walk!",
        "content": """In a hilarious turn of events, the Stellar Strikers' luxury team shuttle
        got stuck in asteroid belt traffic for 6 hours yesterday, forcing players to
        space-walk the final 2 kilometers to their hotel!

        'Best team bonding exercise ever,' laughed star striker Nova Flash. 'Nothing brings
        you together like floating through space with your teammates.'

        The team seemed in good spirits despite the inconvenience, with several players
        posting funny videos of their impromptu spacewalk. Coach Lightning Storm even
        used it as an unplanned training session.

        'If we can handle asteroid traffic, we can handle any opponent,' Storm said.""",
        "tags": ["Stellar Strikers", "travel", "team bonding", "funny", "Nova Flash"],
        "signal_type": "noise",
        "affects_team": None
    },

    {
        "id": 15,
        "date": "2026-04-18",
        "headline": "Cosmic Crusaders Players Seem Nervous About Tomorrow's Match - Body Language Expert Weighs In",
        "content": """We brought in renowned body language expert Dr. Gesture McReadface to analyze footage
        of the Cosmic Crusaders' press conference yesterday, and the results are... concerning for Crusaders fans.

        'Look at how their captain keeps avoiding eye contact when asked about facing Stellar Strikers,'
        Dr. McReadface noted. 'The shoulder tension, the forced smiles - these are classic signs of anxiety.'

        Three players were seen stress-eating at the hotel buffet last night, consuming an estimated 47 donuts
        between them. Is this pre-game fuel or nervous eating? You decide!

        The Crusaders face the league-leading Strikers tomorrow at 18:00. Will their nerves get the better of them?""",
        "tags": ["Cosmic Crusaders", "psychology", "body language", "nerves", "Stellar Strikers"],
        "signal_type": "negative",
        "affects_team": "Cosmic Crusaders"
    },

    {
        "id": 16,
        "date": "2026-04-17",
        "headline": "Nebula Nomads Training Footage Shows INTENSE Practice - 'We're Ready for Anything!'",
        "content": """Leaked training footage from the Nebula Nomads camp shows the team in absolutely
        fierce form ahead of their showdown with Andromeda Asteroids!

        The intensity is off the charts - players were seen running extra drills, practicing penalty kicks
        for hours (smart, given how close these two teams are), and studying game tape until midnight.

        'We respect Andromeda, but we're not scared,' said Nomads midfielder Drift Starling, who seems to
        have overcome their homesickness. 'This is our year!'

        The match is April 19th at 20:00, and with both teams so evenly matched (1.95 vs 2.05 odds),
        it could go either way. Possibly to penalties?""",
        "tags": ["Nebula Nomads", "training", "preparation", "Andromeda Asteroids", "playoffs"],
        "signal_type": "positive",
        "affects_team": "Nebula Nomads"
    },

    {
        "id": 17,
        "date": "2026-04-16",
        "headline": "Pulsar Pirates Already Looking Ahead to Next Season - 'We Know Our Chances'",
        "content": """In a surprisingly honest press conference, Pulsar Pirates captain Skull Darkblade
        admitted the team is already thinking about next year rather than their playoff match against
        Quasar Queens.

        'Look, we're realistic,' Darkblade said with a shrug. 'The Queens are at 1.35 odds and we're at 4.20.
        We're not miracle workers. We're just going to go out there, give it our best, and start planning
        for a better 2027 season.'

        Talk about giving up before the match even starts! While honesty is refreshing, Pirates fans are
        NOT happy with this defeatist attitude.

        One fan comment: 'Why are we even paying to watch if the players don't believe?' Ouch.""",
        "tags": ["Pulsar Pirates", "giving up", "morale", "Quasar Queens", "honesty"],
        "signal_type": "negative",
        "affects_team": "Pulsar Pirates"
    },
]


def get_match_by_id(match_id: int) -> Optional[Dict]:
    """Get a match (completed or upcoming) by its ID."""
    all_matches = PLAYOFF_MATCHES + UPCOMING_MATCHES
    for match in all_matches:
        if match.get("match_id") == match_id:
            return match
    return None


def get_all_completed_matches() -> List[Dict]:
    """Get all completed matches (regular season + playoffs)."""
    completed = []

    # Add regular season matches (no match_id, add one)
    for i, match in enumerate(REGULAR_SEASON_RESULTS):
        m = match.copy()
        m["match_id"] = i + 1
        m["status"] = "completed"
        m["winner"] = (
            match["home"] if match["home_score"] > match["away_score"]
            else match["away"] if match["away_score"] > match["home_score"]
            else "Draw"
        )
        completed.append(m)

    # Add completed playoff matches
    completed.extend([m for m in PLAYOFF_MATCHES if m["status"] == "completed"])

    return completed


def get_upcoming_matches_for_betting() -> List[Dict]:
    """Get upcoming matches available for betting (without revealing actual results).

    Note: Playoff matches don't have Draw option - they go to penalties if tied.
    """
    return [
        {
            "match_id": m["match_id"],
            "round": m["round"],
            "date": m["date"],
            "time": m.get("time", ""),
            "home": m["home"],
            "away": m["away"],
            "odds": {k: v for k, v in m["odds"].items() if k != "Draw"},  # Exclude Draw
            "status": m["status"]
        }
        for m in UPCOMING_MATCHES
    ]


def search_news(keywords: str) -> List[Dict]:
    """Search news articles by keywords."""
    keywords_lower = keywords.lower().split()
    results = []

    for article in PAPARAZZI_NEWS:
        # Search in headline, content, and tags
        searchable = (
            article["headline"].lower() + " " +
            article["content"].lower() + " " +
            " ".join(article["tags"]).lower()
        )

        # Check if any keyword matches
        if any(kw in searchable for kw in keywords_lower):
            # Return without hidden fields
            results.append({
                "id": article["id"],
                "date": article["date"],
                "headline": article["headline"],
                "content": article["content"],
                "tags": article["tags"]
            })

    return sorted(results, key=lambda x: x["date"], reverse=True)
