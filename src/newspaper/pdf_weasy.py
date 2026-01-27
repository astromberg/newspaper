"""PDF generation using WeasyPrint (HTML/CSS based)."""

from __future__ import annotations

import base64
from pathlib import Path

from weasyprint import CSS, HTML

from newspaper.comics import Comic
from newspaper.extras import Joke

# HTML template - edit this to customize layout
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title} - {date}</title>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <div class="date">{date_long}</div>
    </header>

    <main class="comics">
{comics_html}
    </main>
{joke_html}
</body>
</html>
"""

COMIC_TEMPLATE = """        <article class="comic">
            <h2 class="comic-name">{name}</h2>
            <img src="data:image/png;base64,{image_data}" alt="{name}">
        </article>"""

JOKE_TEMPLATE = """
    <section class="joke">
        <h2>Joke of the Day</h2>
        <p class="question">Q: {question}</p>
        <p class="answer">A: {answer}</p>
    </section>"""

# CSS stylesheet - edit this to customize styling
PRINT_CSS = """
@page {
    size: letter;
    margin: 0.5in;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: Helvetica, Arial, sans-serif;
}

header {
    text-align: center;
    margin-bottom: 0.25in;
    padding-bottom: 0.15in;
    border-bottom: 2px solid #333;
}

h1 {
    font-size: 24pt;
    font-weight: bold;
    margin-bottom: 4px;
}

.date {
    font-size: 11pt;
    color: #555;
}

.comics {
    display: block;
}

.comic {
    break-inside: avoid;
    page-break-inside: avoid;
    margin-bottom: 0.25in;
}

.comic-name {
    font-size: 10pt;
    font-weight: bold;
    color: #333;
    margin-bottom: 4px;
}

.comic img {
    width: 100%;
    height: auto;
    border: 1px solid #ddd;
}

.joke {
    break-inside: avoid;
    page-break-inside: avoid;
    margin-top: 0.25in;
    padding: 0.2in;
    background: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.joke h2 {
    font-size: 12pt;
    margin-bottom: 0.1in;
    color: #333;
}

.joke .question {
    font-weight: bold;
    margin-bottom: 0.05in;
}

.joke .answer {
    color: #555;
}
"""


def generate_pdf(
    comics: list[Comic],
    output_path: Path,
    title: str = "The Funny Pages",
    joke: Joke | None = None,
    save_html: bool = False,
) -> None:
    """Generate a printable PDF with comics using WeasyPrint."""
    if not comics:
        print("No comics to generate PDF from!")
        return

    date_str = comics[0].date.isoformat()
    date_long = comics[0].date.strftime("%A, %B %d, %Y")

    # Build comics HTML
    comics_html_parts = []
    for comic in comics:
        img_b64 = base64.b64encode(comic.image_data).decode("utf-8")
        comics_html_parts.append(
            COMIC_TEMPLATE.format(image_data=img_b64, name=comic.name)
        )

    # Build joke HTML
    joke_html = ""
    if joke:
        joke_html = JOKE_TEMPLATE.format(question=joke.question, answer=joke.answer)

    html_content = HTML_TEMPLATE.format(
        title=title,
        date=date_str,
        date_long=date_long,
        comics_html="\n".join(comics_html_parts),
        joke_html=joke_html,
    )

    # Optionally save HTML for debugging/preview
    if save_html:
        html_path = output_path.with_suffix(".html")
        # Inject CSS into HTML for standalone viewing
        styled_html = html_content.replace(
            "</head>",
            f"<style>{PRINT_CSS}</style>\n</head>"
        )
        html_path.write_text(styled_html)
        print(f"HTML saved to: {html_path}")

    # Generate PDF with WeasyPrint
    html = HTML(string=html_content)
    css = CSS(string=PRINT_CSS)
    html.write_pdf(output_path, stylesheets=[css])

    print(f"PDF saved to: {output_path}")
