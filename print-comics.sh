#!/bin/bash
# Daily comics printer script
# Add to cron: 0 6 * * * /path/to/newspaper/print-comics.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
PRINTER=""  # Leave empty for default, or set to printer name

# WeasyPrint library path (macOS with Homebrew - not needed on Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
    export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
fi

# Generate today's comics as PDF
echo "$(date): Generating comics..."
~/.local/bin/uv run newspaper --format pdf

# Get today's filename
TODAY=$(date +%Y-%m-%d)
PDF_FILE="funny-pages-${TODAY}.pdf"

# Print it
if [ -f "$PDF_FILE" ]; then
    echo "$(date): Printing $PDF_FILE..."
    # Print double-sided (duplex)
    if [ -n "$PRINTER" ]; then
        lp -d "$PRINTER" -o sides=two-sided-long-edge "$PDF_FILE"
    else
        lp -o sides=two-sided-long-edge "$PDF_FILE"
    fi

    # Optional: remove after printing (uncomment to enable)
    # rm "$PDF_FILE"

    echo "$(date): Successfully printed $PDF_FILE"
else
    echo "$(date): ERROR - PDF file not generated: $PDF_FILE"
    exit 1
fi
