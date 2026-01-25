# newspaper

A CLI tool that generates printable "funny pages" for kids - a daily collection of comic strips from GoComics and The Far Side.

## Features

- Fetches comics from GoComics (Calvin and Hobbes, Peanuts, Garfield, etc.)
- Fetches The Far Side from thefarside.com
- Supports archive comics that cycle through historical strips (Ozy and Millie)
- Outputs PDF or HTML formats
- Customizable layout (columns, title)
- Automation-ready with print script for daily cron jobs

## Installation

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/yourusername/newspaper.git
cd newspaper
uv sync
```

## Usage

```bash
# Generate today's comics as PDF
uv run newspaper

# Generate as HTML (easier to customize)
uv run newspaper --format html

# Custom title
uv run newspaper --title "Emma's Daily Comics"

# Different column layout (HTML only)
uv run newspaper --format html --columns 3

# Specific date
uv run newspaper --date 2024-01-15

# List available comics
uv run newspaper --list
```

## Included Comics

- Calvin and Hobbes
- Peanuts
- Garfield
- Big Nate
- FoxTrot Classics
- Zits
- Baby Blues
- Pearls Before Swine
- Ozy and Millie (archive - cycles from beginning)
- Phoebe and Her Unicorn
- The Far Side

## Automation

To print comics automatically each morning:

1. Edit `print-comics.sh` and set your email address
2. Set up a cron job:

```bash
crontab -e
# Add: 0 6 * * * /path/to/newspaper/print-comics.sh >> /path/to/newspaper/cron.log 2>&1
```

The script will email you if anything fails.

## Configuration

Archive comic positions are stored in `~/.newspaper_state.json`. Each run advances to the next strip.

## License

MIT
