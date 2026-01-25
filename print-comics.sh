#!/bin/bash
# Daily comics printer script
# Add to cron: 0 6 * * * /path/to/newspaper/print-comics.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
EMAIL="your-email@example.com"  # Change this to your email
PRINTER=""  # Leave empty for default, or set to printer name

# Function to send failure email
send_failure_email() {
    local error_msg="$1"
    echo "Comics generation/printing failed at $(date): $error_msg" | \
        mail -s "🚨 Daily Comics Failed" "$EMAIL"
}

# Trap errors and send email
trap 'send_failure_email "Script failed on line $LINENO"' ERR

# Generate today's comics as HTML
echo "$(date): Generating comics..."
~/.local/bin/uv run newspaper --format html

# Get today's filename
TODAY=$(date +%Y-%m-%d)
HTML_FILE="funny-pages-${TODAY}.html"
PDF_FILE="funny-pages-${TODAY}.pdf"

# Convert HTML to PDF using headless Chrome
echo "$(date): Converting HTML to PDF..."
chromium-browser --headless --print-to-pdf="$PDF_FILE" --no-margins "$HTML_FILE" 2>/dev/null \
    || google-chrome --headless --print-to-pdf="$PDF_FILE" --no-margins "$HTML_FILE" 2>/dev/null \
    || chromium --headless --print-to-pdf="$PDF_FILE" --no-margins "$HTML_FILE" 2>/dev/null

# Print it
if [ -f "$PDF_FILE" ]; then
    echo "$(date): Printing $PDF_FILE..."
    if [ -n "$PRINTER" ]; then
        lp -d "$PRINTER" "$PDF_FILE"
    else
        lp "$PDF_FILE"
    fi

    # Optional: remove after printing (uncomment to enable)
    # rm "$PDF_FILE" "$HTML_FILE"

    echo "$(date): Successfully printed $PDF_FILE"
else
    send_failure_email "PDF file not generated: $PDF_FILE"
    exit 1
fi
