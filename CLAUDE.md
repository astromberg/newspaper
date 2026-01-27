# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Generate today's funny pages (macOS needs library path for WeasyPrint)
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib uv run newspaper

# Generate for a specific date
uv run newspaper --date 2024-01-15

# Output to specific file
uv run newspaper -o my-comics.pdf

# List available comics
uv run newspaper --list

# Save HTML alongside PDF for preview/debugging
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib uv run newspaper --save-html

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
- `src/newspaper/pdf_weasy.py` - PDF generation using WeasyPrint (HTML/CSS based)
- `src/newspaper/pdf.py` - Legacy PDF generation with reportlab (not currently used)
- `src/newspaper/extras.py` - Weather, jokes, sports data fetching (not currently used)
- `tests/` - Test files

Comics are fetched by scraping GoComics pages for image URLs, then rendered to PDF via WeasyPrint.

## Customizing Layout

Edit `src/newspaper/pdf_weasy.py` to customize the layout:
- `HTML_TEMPLATE` - Page structure
- `COMIC_TEMPLATE` - Individual comic markup
- `PRINT_CSS` - Styling (standard CSS with `@page` rules)

Use `--save-html` flag to preview HTML in browser before PDF conversion.

## macOS Setup

WeasyPrint requires Pango. Install via Homebrew:
```bash
brew install pango
```

Set library path when running:
```bash
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
```
