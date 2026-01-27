"""Extra newspaper features: weather, jokes, sports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from urllib.parse import quote

import httpx

# Configuration
WEATHER_LOCATION = "Belmont,CA,USA"
FAVORITE_TEAMS = {
    "mlb": ["San Francisco Giants"],
    "nfl": ["Denver Broncos", "San Francisco 49ers"],
    "nba": ["Golden State Warriors"],
}


# Kid-friendly jokes and riddles (about 100 to last ~3 months without repeats)
JOKES = [
    # Classic puns
    ("Why don't scientists trust atoms?", "Because they make up everything!"),
    ("What do you call a fish without eyes?", "A fsh!"),
    ("Why did the scarecrow win an award?", "He was outstanding in his field!"),
    ("What do you call a bear with no teeth?", "A gummy bear!"),
    ("Why don't eggs tell jokes?", "They'd crack each other up!"),
    ("What do you call a dinosaur that crashes their car?", "Tyrannosaurus Wrecks!"),
    ("Why did the bicycle fall over?", "Because it was two-tired!"),
    ("What do you call a sleeping dinosaur?", "A dino-snore!"),
    ("Why did the cookie go to the doctor?", "Because it was feeling crummy!"),
    ("What do you call a dog magician?", "A Labracadabrador!"),
    ("Why did the math book look sad?", "It had too many problems!"),
    ("What do you call cheese that isn't yours?", "Nacho cheese!"),
    ("Why can't you give Elsa a balloon?", "Because she'll let it go!"),
    ("What did the ocean say to the beach?", "Nothing, it just waved!"),
    ("What do you call a cow with no legs?", "Ground beef!"),
    ("Why did the banana go to the doctor?", "It wasn't peeling well!"),
    ("What do you call a boomerang that doesn't come back?", "A stick!"),
    ("Why are ghosts bad liars?", "You can see right through them!"),
    ("What did one wall say to the other?", "I'll meet you at the corner!"),
    ("Why did the golfer bring two pairs of pants?", "In case he got a hole in one!"),
    ("What do you call a pig that does karate?", "A pork chop!"),
    ("Why couldn't the pony sing?", "Because she was a little horse!"),
    ("What do you call a cow on a trampoline?", "A milkshake!"),
    ("Why did the teddy bear say no to dessert?", "She was already stuffed!"),
    ("What did the left eye say to the right eye?", "Between us, something smells!"),
    ("Why do bees have sticky hair?", "Because they use honeycombs!"),
    ("What do you call a fake noodle?", "An impasta!"),
    ("Why did the kid throw a clock out the window?", "To see time fly!"),
    ("What do you call a snowman with a six-pack?", "An abdominal snowman!"),
    # Animals
    ("What do you call an alligator in a vest?", "An investigator!"),
    ("Why do cows wear bells?", "Because their horns don't work!"),
    ("What do you call a fly without wings?", "A walk!"),
    ("Why don't oysters share?", "Because they're shellfish!"),
    ("What do you call a lazy kangaroo?", "A pouch potato!"),
    ("Why do seagulls fly over the sea?", "If they flew over the bay, they'd be bagels!"),  # noqa: E501
    ("What do you call a fish that wears a crown?", "A king fish!"),
    ("Why did the chicken join a band?", "Because it had the drumsticks!"),
    ("What do you get when you cross a snake and a pie?", "A pie-thon!"),
    ("What do you call a deer with no eyes?", "No idea!"),
    ("Why do ducks have tail feathers?", "To cover their butt quacks!"),
    ("What do you call a cat that gets anything it wants?", "Purrr-suasive!"),
    ("Why did the turtle cross the road?", "To get to the Shell station!"),
    ("What do you call a monkey at the North Pole?", "Lost!"),
    ("Why do hummingbirds hum?", "Because they don't know the words!"),
    # Food
    ("Why did the tomato turn red?", "Because it saw the salad dressing!"),
    ("What do you call a sad strawberry?", "A blueberry!"),
    ("Why did the orange stop rolling?", "It ran out of juice!"),
    ("What's a ghost's favorite fruit?", "Boo-berries!"),
    ("Why did the lemon go to the doctor?", "It wasn't peeling well!"),
    ("What do you call a grumpy cow?", "Moody!"),
    ("Why did the grape stop in the middle of the road?", "It ran out of juice!"),
    ("What's a vampire's favorite fruit?", "A blood orange!"),
    ("Why did the mushroom go to the party?", "Because he was a fungi!"),
    ("What do you call a piece of bread on the moon?", "Space toast!"),
    # School
    ("Why did the student eat his homework?", "The teacher said it was a piece of cake!"),  # noqa: E501
    ("What's a math teacher's favorite season?", "Sum-mer!"),
    ("Why did the music teacher go to jail?", "She got caught with too many sharps!"),
    ("What do you call a teacher who forgot to take attendance?", "Absent-minded!"),
    ("Why was the geometry book so sad?", "It had too many problems!"),
    ("What did the pencil say to the paper?", "I dot my i's on you!"),
    ("Why did the kid bring a ladder to school?", "To go to high school!"),
    ("What's the king of all school supplies?", "The ruler!"),
    # Nature & Space
    ("How do trees access the internet?", "They log in!"),
    ("What did the big flower say to the little flower?", "Hey there, bud!"),
    ("Why did the sun go to school?", "To get a little brighter!"),
    ("What do planets like to read?", "Comet books!"),
    ("Why did the moon burp?", "Because it was full!"),
    ("What kind of music do planets like?", "Neptunes!"),
    ("How does the ocean say hello?", "It waves!"),
    ("What did one volcano say to the other?", "I lava you!"),
    ("Why is grass so dangerous?", "Because it's full of blades!"),
    # Sports
    ("Why did the football coach go to the bank?", "To get his quarterback!"),
    ("What's a boxer's favorite drink?", "Punch!"),
    ("Why are basketball players messy eaters?", "They're always dribbling!"),
    ("What do you call a boomerang that won't come back?", "A stick!"),
    ("Why did the golfer wear two pairs of pants?", "In case he got a hole in one!"),
    ("What lights up a soccer stadium?", "A soccer match!"),
    ("Why can't Cinderella play soccer?", "Because she always runs from the ball!"),
    # Everyday objects
    ("What did the stamp say to the envelope?", "Stick with me and we'll go places!"),
    ("Why did the belt go to jail?", "For holding up pants!"),
    ("What did the hat say to the scarf?", "You hang around, I'll go on ahead!"),
    ("Why did the phone wear glasses?", "Because it lost its contacts!"),
    ("What do you call a sleeping bull?", "A bulldozer!"),
    ("Why did the picture go to jail?", "Because it was framed!"),
    ("What did the blanket say to the bed?", "I've got you covered!"),
    ("Why was the broom late?", "It over-swept!"),
    # Knock-knock style (as Q&A)
    ("What do you get if you cross a snowman with a vampire?", "Frostbite!"),
    ("What do you get when you cross a centipede with a parrot?", "A walkie talkie!"),
    ("What do you get when you cross a robot and a tractor?", "A trans-farmer!"),
    # More silly ones
    ("Why do bicycles fall over?", "Because they're two-tired!"),
    ("What do you call a train carrying bubblegum?", "A chew-chew train!"),
    ("Why did the computer go to the doctor?", "Because it had a virus!"),
    ("What do you call a funny mountain?", "Hill-arious!"),
    ("Why did the nose feel sad?", "It was always getting picked on!"),
    ("What do elves learn in school?", "The elf-abet!"),
    ("Why was the baby strawberry crying?", "Because its parents were in a jam!"),
    ("What do you call a dinosaur that is sleeping?", "A dino-snore!"),
    ("Why did the melon jump into the lake?", "It wanted to be a watermelon!"),
    ("What has ears but cannot hear?", "A cornfield!"),
    ("Why do sharks swim in salt water?", "Because pepper water makes them sneeze!"),
    ("What do you call a dog that does magic tricks?", "A Labracadabrador!"),
    ("Why did the can crusher quit his job?", "Because it was soda pressing!"),
    ("What's brown and sticky?", "A stick!"),
    ("Why couldn't the leopard play hide and seek?", "Because he was always spotted!"),
]


@dataclass
class Weather:
    """Weather data."""

    location: str
    temperature: int  # Fahrenheit
    condition: str
    high: int
    low: int
    humidity: int


@dataclass
class Joke:
    """A joke or riddle."""

    question: str
    answer: str


@dataclass
class SportsStandings:
    """Sports standings for a division."""

    league: str
    division: str
    teams: list[tuple[str, str, str]]  # (name, wins-losses, games_back)
    favorite_team: str | None


@dataclass
class RecentGame:
    """A recent game result."""

    date: str
    opponent: str
    home: bool  # True if home game
    won: bool
    team_score: int
    opponent_score: int


@dataclass
class TeamRecent:
    """Recent games for a favorite team."""

    team_name: str
    record: str  # e.g. "25-22"
    games: list[RecentGame]


@dataclass
class UpcomingGame:
    """An upcoming important game."""

    date: str
    time: str
    home_team: str
    away_team: str
    note: str  # e.g. "Super Bowl LX"


@dataclass
class BaseballCountdown:
    """Countdown to baseball season."""

    days_to_spring_training: int | None  # None if already started
    days_to_opening_day: int | None  # None if season started
    spring_training_date: date
    opening_day_date: date


async def fetch_baseball_countdown() -> BaseballCountdown | None:
    """Fetch MLB season dates and calculate countdown."""
    today = date.today()
    year = today.year

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://statsapi.mlb.com/api/v1/seasons/{year}?sportId=1"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            seasons = data.get("seasons", [])
            if not seasons:
                return None

            season = seasons[0]
            spring_start_str = season.get("springStartDate")
            regular_start_str = season.get("regularSeasonStartDate")

            if not spring_start_str or not regular_start_str:
                return None

            # Parse dates (format: YYYY-MM-DD)
            spring_start = date.fromisoformat(spring_start_str)
            opening_day = date.fromisoformat(regular_start_str)

            # If we're past opening day, no countdown needed
            if today >= opening_day:
                return None

            days_to_spring = None
            if today < spring_start:
                days_to_spring = (spring_start - today).days

            days_to_opening = None
            if today < opening_day:
                days_to_opening = (opening_day - today).days

            return BaseballCountdown(
                days_to_spring_training=days_to_spring,
                days_to_opening_day=days_to_opening,
                spring_training_date=spring_start,
                opening_day_date=opening_day,
            )
    except Exception as e:
        print(f"  Warning: Could not fetch MLB season dates: {e}")
        return None


async def fetch_weather(location: str = WEATHER_LOCATION) -> Weather | None:
    """Fetch current weather for a location using wttr.in."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Use wttr.in which is free and doesn't need an API key
            # URL encode the location to handle commas
            encoded_location = quote(location, safe="")
            url = f"https://wttr.in/{encoded_location}?format=j1"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            current = data["current_condition"][0]
            weather_desc = current["weatherDesc"][0]["value"]
            temp_f = int(current["temp_F"])
            humidity = int(current["humidity"])

            # Get today's forecast for high/low
            today = data["weather"][0]
            high = int(today["maxtempF"])
            low = int(today["mintempF"])

            location = data["nearest_area"][0]["areaName"][0]["value"]

            return Weather(
                location=location,
                temperature=temp_f,
                condition=weather_desc,
                high=high,
                low=low,
                humidity=humidity,
            )
    except Exception as e:
        print(f"  Warning: Could not fetch weather: {e}")
        return None


def get_daily_joke() -> Joke:
    """Get today's joke based on day of year, cycling through all jokes."""
    today = date.today()
    index = today.timetuple().tm_yday % len(JOKES)
    question, answer = JOKES[index]
    return Joke(question=question, answer=answer)


async def fetch_mlb_standings() -> list[SportsStandings]:
    """Fetch MLB standings."""
    standings = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = "https://site.api.espn.com/apis/v2/sports/baseball/mlb/standings"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            for group in data.get("children", []):
                for division in group.get("children", []):
                    div_name = division.get("name", "Unknown")
                    teams = []
                    favorite = None

                    for entry in division.get("standings", {}).get("entries", []):
                        team_name = entry.get("team", {}).get("displayName", "Unknown")
                        stats = {s["name"]: s["value"] for s in entry.get("stats", [])}
                        wins = int(stats.get("wins", 0))
                        losses = int(stats.get("losses", 0))
                        gb = stats.get("gamesBehind", "-")
                        if gb == 0:
                            gb = "-"

                        teams.append((team_name, f"{wins}-{losses}", str(gb)))

                        if team_name in FAVORITE_TEAMS["mlb"]:
                            favorite = team_name

                    standings.append(SportsStandings(
                        league="MLB",
                        division=div_name,
                        teams=teams[:5],  # Top 5 teams
                        favorite_team=favorite,
                    ))
    except Exception as e:
        print(f"  Warning: Could not fetch MLB standings: {e}")

    return standings


async def fetch_nfl_standings() -> list[SportsStandings]:
    """Fetch NFL standings."""
    standings = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = "https://site.api.espn.com/apis/v2/sports/football/nfl/standings"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            for group in data.get("children", []):
                for division in group.get("children", []):
                    div_name = division.get("name", "Unknown")
                    teams = []
                    favorite = None

                    for entry in division.get("standings", {}).get("entries", []):
                        team_name = entry.get("team", {}).get("displayName", "Unknown")
                        stats = {s["name"]: s["value"] for s in entry.get("stats", [])}
                        wins = int(stats.get("wins", 0))
                        losses = int(stats.get("losses", 0))

                        teams.append((team_name, f"{wins}-{losses}", ""))

                        if team_name in FAVORITE_TEAMS["nfl"]:
                            favorite = team_name

                    standings.append(SportsStandings(
                        league="NFL",
                        division=div_name,
                        teams=teams,
                        favorite_team=favorite,
                    ))
    except Exception as e:
        print(f"  Warning: Could not fetch NFL standings: {e}")

    return standings


async def fetch_warriors_recent(num_games: int = 4) -> TeamRecent | None:
    """Fetch Warriors recent games with scores."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Team ID 9 = Golden State Warriors
            url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/9/schedule"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            team_name = data.get("team", {}).get("displayName", "Warriors")

            # Get completed games
            events = data.get("events", [])
            completed = []
            for e in events:
                comp = e.get("competitions", [{}])[0]
                if comp.get("status", {}).get("type", {}).get("completed", False):
                    completed.append(e)

            # Get last N games
            recent_events = completed[-num_games:] if completed else []
            games = []
            total_wins = 0
            total_losses = 0

            for event in recent_events:
                comp = event.get("competitions", [{}])[0]
                competitors = comp.get("competitors", [])
                if len(competitors) < 2:
                    continue

                # Find Warriors and opponent
                gsw = None
                opp = None
                for c in competitors:
                    if c.get("team", {}).get("id") == "9":
                        gsw = c
                    else:
                        opp = c

                if not gsw or not opp:
                    continue

                # Get scores (handle dict format)
                gsw_score_raw = gsw.get("score", 0)
                opp_score_raw = opp.get("score", 0)
                if isinstance(gsw_score_raw, dict):
                    gsw_score = int(gsw_score_raw.get("value", 0))
                else:
                    gsw_score = int(gsw_score_raw) if gsw_score_raw else 0
                if isinstance(opp_score_raw, dict):
                    opp_score = int(opp_score_raw.get("value", 0))
                else:
                    opp_score = int(opp_score_raw) if opp_score_raw else 0

                won = gsw.get("winner", False)
                is_home = gsw.get("homeAway", "") == "home"
                opp_name = opp.get("team", {}).get("shortDisplayName", "???")
                game_date = event.get("date", "")[:10]

                games.append(RecentGame(
                    date=game_date,
                    opponent=opp_name,
                    home=is_home,
                    won=won,
                    team_score=gsw_score,
                    opponent_score=opp_score,
                ))

                if won:
                    total_wins += 1
                else:
                    total_losses += 1

            # Get overall record from standings
            standings_url = "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings"
            resp = await client.get(standings_url)
            resp.raise_for_status()
            standings_data = resp.json()
            record = "?-?"
            for group in standings_data.get("children", []):
                for entry in group.get("standings", {}).get("entries", []):
                    if entry.get("team", {}).get("id") == "9":
                        stats = {}
                        for s in entry.get("stats", []):
                            if "value" in s:
                                stats[s["name"]] = s["value"]
                        wins = int(stats.get("wins", 0))
                        losses = int(stats.get("losses", 0))
                        record = f"{wins}-{losses}"
                        break

            return TeamRecent(
                team_name=team_name,
                record=record,
                games=games,
            )
    except Exception as e:
        print(f"  Warning: Could not fetch Warriors games: {e}")
        return None


async def fetch_nfl_upcoming() -> list[UpcomingGame]:
    """Fetch upcoming NFL playoff/important games."""
    games = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check current week scoreboard
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            season_type = data.get("season", {}).get("type", 1)

            # Only show playoff games (season type 3)
            if season_type != 3:
                return games

            for event in data.get("events", []):
                comp = event.get("competitions", [{}])[0]
                status = comp.get("status", {}).get("type", {})

                # Skip completed games
                if status.get("completed", False):
                    continue

                competitors = comp.get("competitors", [])
                if len(competitors) < 2:
                    continue

                home = None
                away = None
                for c in competitors:
                    if c.get("homeAway") == "home":
                        home = c
                    else:
                        away = c

                if not home or not away:
                    continue

                home_name = home.get("team", {}).get("displayName", "???")
                away_name = away.get("team", {}).get("displayName", "???")

                event_date = event.get("date", "")
                game_date = event_date[:10]
                game_time = event_date[11:16] if "T" in event_date else ""

                notes = comp.get("notes", [])
                note = notes[0].get("headline", "") if notes else "Playoff Game"

                games.append(UpcomingGame(
                    date=game_date,
                    time=game_time,
                    home_team=home_name,
                    away_team=away_name,
                    note=note,
                ))

            # Also check for Super Bowl (week 5 of postseason)
            if not games:
                sb_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?week=5&seasontype=3"
                sb_resp = await client.get(sb_url)
                if sb_resp.status_code == 200:
                    sb_data = sb_resp.json()
                    for event in sb_data.get("events", []):
                        comp = event.get("competitions", [{}])[0]
                        status = comp.get("status", {}).get("type", {})

                        if status.get("completed", False):
                            continue

                        competitors = comp.get("competitors", [])
                        if len(competitors) < 2:
                            continue

                        home = None
                        away = None
                        for c in competitors:
                            if c.get("homeAway") == "home":
                                home = c
                            else:
                                away = c

                        if not home or not away:
                            continue

                        home_name = home.get("team", {}).get("displayName", "???")
                        away_name = away.get("team", {}).get("displayName", "???")

                        event_date = event.get("date", "")
                        game_date = event_date[:10]
                        game_time = event_date[11:16] if "T" in event_date else ""

                        notes = comp.get("notes", [])
                        note = notes[0].get("headline", "") if notes else "Super Bowl"

                        games.append(UpcomingGame(
                            date=game_date,
                            time=game_time,
                            home_team=home_name,
                            away_team=away_name,
                            note=note,
                        ))

    except Exception as e:
        print(f"  Warning: Could not fetch NFL upcoming games: {e}")

    return games


@dataclass
class SportsData:
    """All sports data for the newspaper."""

    standings: list[SportsStandings]
    warriors_recent: TeamRecent | None
    nfl_upcoming: list[UpcomingGame]
    baseball_countdown: BaseballCountdown | None


async def fetch_all_sports() -> SportsData:
    """Fetch all sports data."""
    all_standings = []

    print("  Fetching MLB standings...")
    mlb = await fetch_mlb_standings()
    # Only include divisions with our teams
    all_standings.extend([s for s in mlb if s.favorite_team])

    print("  Fetching NFL standings...")
    nfl = await fetch_nfl_standings()
    all_standings.extend([s for s in nfl if s.favorite_team])

    print("  Fetching NFL upcoming games...")
    nfl_upcoming = await fetch_nfl_upcoming()

    print("  Fetching Warriors recent games...")
    warriors = await fetch_warriors_recent()

    # Get baseball countdown from MLB API
    print("  Fetching MLB season dates...")
    baseball_countdown = await fetch_baseball_countdown()

    return SportsData(
        standings=all_standings,
        warriors_recent=warriors,
        nfl_upcoming=nfl_upcoming,
        baseball_countdown=baseball_countdown,
    )
