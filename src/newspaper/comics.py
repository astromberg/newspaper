"""Comic fetching from various sources."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import httpx

# State file for tracking archive comic positions
STATE_FILE = Path.home() / ".newspaper_state.json"

# Archive comics: (name, start_date, end_date)
# These cycle through historical strips instead of fetching today's date
ARCHIVE_COMICS = {
    "ozy-and-millie": ("Ozy and Millie", date(2022, 2, 1), date(2025, 12, 31)),
    "foxtrotclassics": ("FoxTrot Classics", date(2020, 1, 1), date(2025, 12, 31)),
}

# Far Side configuration
FARSIDE_NAME = "The Far Side"

# Default comics to fetch (GoComics slugs)
DEFAULT_COMICS = [
    ("calvinandhobbes", "Calvin and Hobbes"),
    ("peanuts", "Peanuts"),
    ("garfield", "Garfield"),
    ("bignate", "Big Nate"),
    ("foxtrotclassics", "FoxTrot Classics"),
    ("babyblues", "Baby Blues"),
    ("pearlsbeforeswine", "Pearls Before Swine"),
    ("ozy-and-millie", "Ozy and Millie"),
    ("phoebe-and-her-unicorn", "Phoebe and Her Unicorn"),
    ("shermanslagoon", "Sherman's Lagoon"),
    ("forbetterorforworse", "For Better Or Worse"),
    ("farside", "The Far Side"),
]


@dataclass
class Comic:
    """A fetched comic strip."""

    name: str
    slug: str
    image_data: bytes
    date: date


def load_state() -> dict:
    """Load the state file for archive comics."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict) -> None:
    """Save the state file for archive comics."""
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_archive_date(slug: str) -> date:
    """Get the current date for an archive comic, advancing it for next time."""
    state = load_state()
    name, start_date, end_date = ARCHIVE_COMICS[slug]

    # Get current position or start from beginning
    key = f"archive_{slug}"
    if key in state:
        current = date.fromisoformat(state[key])
        # Advance to next day
        next_date = current + timedelta(days=1)
        # Loop back to start if we've reached the end
        if next_date > end_date:
            next_date = start_date
    else:
        next_date = start_date

    # Save the new position
    state[key] = next_date.isoformat()
    save_state(state)

    return next_date


async def fetch_gocomics(
    client: httpx.AsyncClient, slug: str, name: str, comic_date: date
) -> Comic | None:
    """Fetch a comic strip from GoComics."""
    url = (
        f"https://www.gocomics.com/{slug}/"
        f"{comic_date.year}/{comic_date.month:02d}/{comic_date.day:02d}"
    )

    try:
        response = await client.get(url)
        response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"  Warning: Could not fetch {name}: {e}")
        return None

    # Find the comic image - look for the main comic image in srcSet
    # Pattern: featureassets.gocomics.com/assets/{id}?optimizer=...
    pattern = r'Comic_comic__image[^>]*srcSet="([^"]+)"'
    match = re.search(pattern, response.text)

    if match:
        srcset = match.group(1).replace("&amp;", "&")
        # Extract the asset ID and build a high-quality URL
        asset_match = re.search(r'/assets/([a-f0-9]+)\?', srcset)
        if asset_match:
            asset_id = asset_match.group(1)
            image_url = (
                f"https://featureassets.gocomics.com/assets/{asset_id}"
                "?optimizer=image&width=900&quality=85"
            )
        else:
            print(f"  Warning: Could not parse asset ID for {name}")
            return None
    else:
        # Fallback: try old pattern
        old_pattern = r'(https://assets\.amuniversal\.com/[a-f0-9]+)'
        old_match = re.search(old_pattern, response.text)
        if old_match:
            image_url = old_match.group(1)
        else:
            print(f"  Warning: Could not find image for {name}")
            return None

    try:
        img_response = await client.get(image_url)
        img_response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"  Warning: Could not download image for {name}: {e}")
        return None

    return Comic(name=name, slug=slug, image_data=img_response.content, date=comic_date)


async def fetch_farside(client: httpx.AsyncClient) -> Comic | None:
    """Fetch today's Far Side comic from thefarside.com."""
    url = "https://www.thefarside.com"

    try:
        response = await client.get(url)
        response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"  Warning: Could not fetch The Far Side: {e}")
        return None

    # Find the comic image URL - look for splash_images in the CDN
    pattern = r'(https://siteassets\.thefarside\.com/uploads/splash_images/[^"\'>\s]+)'
    match = re.search(pattern, response.text)

    if not match:
        print("  Warning: Could not find image for The Far Side")
        return None

    image_url = match.group(1)

    try:
        img_response = await client.get(image_url)
        img_response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"  Warning: Could not download image for The Far Side: {e}")
        return None

    return Comic(
        name=FARSIDE_NAME,
        slug="farside",
        image_data=img_response.content,
        date=date.today(),
    )


async def fetch_comic(
    client: httpx.AsyncClient, slug: str, name: str, comic_date: date
) -> Comic | None:
    """Fetch a single comic strip from the appropriate source."""
    # Handle Far Side specially
    if slug == "farside":
        return await fetch_farside(client)

    # Handle archive comics (use their own date progression)
    if slug in ARCHIVE_COMICS:
        archive_date = get_archive_date(slug)
        print(f"    (archive: {archive_date.strftime('%Y-%m-%d')})")
        return await fetch_gocomics(client, slug, name, archive_date)

    # Regular GoComics
    return await fetch_gocomics(client, slug, name, comic_date)


async def fetch_comics(
    comic_date: date | None = None,
    comics: list[tuple[str, str]] | None = None,
) -> list[Comic]:
    """Fetch all comics for a given date."""
    if comic_date is None:
        comic_date = date.today()

    if comics is None:
        comics = DEFAULT_COMICS

    print(f"Fetching comics for {comic_date.strftime('%B %d, %Y')}...")

    fetched: list[Comic] = []

    async with httpx.AsyncClient(
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        },
        follow_redirects=True,
        timeout=30.0,
    ) as client:
        for slug, name in comics:
            print(f"  Fetching {name}...")
            comic = await fetch_comic(client, slug, name, comic_date)
            if comic:
                fetched.append(comic)

    print(f"Successfully fetched {len(fetched)} of {len(comics)} comics")
    return fetched
