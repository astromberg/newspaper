#!/bin/bash
# Daily comics printer script
# Add to cron: 0 6 * * * /path/to/newspaper/print-comics.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
PRINTER=""  # Leave empty for default, or set to printer name

# Generate today's comics as HTML
echo "$(date): Generating comics..."
~/.local/bin/uv run newspaper --format html --columns 1

# Get today's filename
TODAY=$(date +%Y-%m-%d)
HTML_FILE="funny-pages-${TODAY}.html"
PDF_FILE="funny-pages-${TODAY}.pdf"

# Convert HTML to PDF using headless Chrome
echo "$(date): Converting HTML to PDF..."
CHROME_FLAGS="--headless --disable-gpu --no-sandbox --disable-software-rasterizer --disable-dev-shm-usage --password-store=basic --print-to-pdf=$PDF_FILE --no-pdf-header-footer"

chromium-browser $CHROME_FLAGS "$HTML_FILE" 2>/dev/null \
    || google-chrome $CHROME_FLAGS "$HTML_FILE" 2>/dev/null \
    || chromium $CHROME_FLAGS "$HTML_FILE" 2>/dev/null \
    || google-chrome-stable $CHROME_FLAGS "$HTML_FILE" 2>/dev/null

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
    # rm "$PDF_FILE" "$HTML_FILE"

    echo "$(date): Successfully printed $PDF_FILE"
else
    echo "$(date): ERROR - PDF file not generated: $PDF_FILE"
    exit 1
fi
