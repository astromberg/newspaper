# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Generate today's funny pages
uv run newspaper

# Generate for a specific date
uv run newspaper --date 2024-01-15

# Output to specific file
uv run newspaper -o my-comics.pdf

# List available comics
uv run newspaper --list

# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_cli.py::test_name

# Lint and format
uv run ruff check src tests
uv run ruff format src tests
```

## Architecture

CLI tool that fetches comic strips from GoComics and generates a printable PDF.

- `src/newspaper/cli.py` - CLI entry point, argument parsing
- `src/newspaper/comics.py` - Async comic fetching from GoComics, `DEFAULT_COMICS` list
- `src/newspaper/pdf.py` - PDF generation with reportlab, 2-column layout
- `tests/` - Test files

Comics are fetched by scraping GoComics pages for image URLs, then arranged in a 2-column grid on a letter-sized PDF.
