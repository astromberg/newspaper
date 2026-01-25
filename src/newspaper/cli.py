"""Command-line interface for newspaper."""

import argparse
import asyncio
from datetime import date, datetime
from pathlib import Path

from newspaper.comics import DEFAULT_COMICS, fetch_comics
from newspaper.html import generate_html
from newspaper.pdf import generate_pdf


def parse_date(date_str: str) -> date:
    """Parse a date string in YYYY-MM-DD format."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="newspaper",
        description="Generate a printable funny pages for kids",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    parser.add_argument(
        "-d", "--date",
        type=parse_date,
        default=None,
        help="Date to fetch comics for (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output file path. Defaults to funny-pages-YYYY-MM-DD.{format}",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["pdf", "html"],
        default="pdf",
        help="Output format: pdf or html (default: pdf)",
    )
    parser.add_argument(
        "-c", "--columns",
        type=int,
        default=2,
        help="Number of columns (default: 2, HTML only)",
    )
    parser.add_argument(
        "-t", "--title",
        type=str,
        default="The Funny Pages",
        help="Custom title for the page (default: 'The Funny Pages')",
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List available comics and exit",
    )

    args = parser.parse_args()

    if args.list:
        print("Available comics:")
        for slug, name in DEFAULT_COMICS:
            print(f"  {slug}: {name}")
        return

    comic_date = args.date or date.today()
    ext = args.format
    output_path = args.output or Path(f"funny-pages-{comic_date.isoformat()}.{ext}")

    # Fetch comics and generate output
    comics = asyncio.run(fetch_comics(comic_date))

    if comics:
        if args.format == "html":
            generate_html(comics, output_path, columns=args.columns, title=args.title)
        else:
            generate_pdf(comics, output_path, title=args.title)
        print(f"\nDone! Print {output_path} for your kids.")
    else:
        print("\nNo comics could be fetched. Check your internet connection.")


if __name__ == "__main__":
    main()
