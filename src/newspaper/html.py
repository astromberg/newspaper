"""HTML generation for the funny pages."""

from __future__ import annotations

import base64
from pathlib import Path

from newspaper.comics import Comic

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {date}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: Georgia, 'Times New Roman', serif;
            max-width: 8in;
            margin: 0 auto;
            padding: 0.25in;
            background: white;
        }}

        header {{
            text-align: center;
            margin-bottom: 0.3in;
            border-bottom: 2px solid #333;
            padding-bottom: 0.15in;
        }}

        h1 {{
            font-size: 32pt;
            font-weight: bold;
            margin-bottom: 4px;
        }}

        .date {{
            font-size: 12pt;
            color: #555;
        }}

        .comics {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        .comic {{
            width: 100%;
            break-inside: avoid;
            page-break-inside: avoid;
            margin-bottom: 0.3in;
            text-align: center;
        }}

        .comic img {{
            width: 100%;
            height: auto;
            border: 1px solid #ccc;
        }}

        .comic-name {{
            font-size: 11pt;
            font-weight: bold;
            margin-bottom: 4px;
            color: #333;
            text-align: left;
        }}

        @page {{
            margin: 0.5in;
        }}

        @media print {{
            body {{
                padding: 0;
                max-width: none;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <div class="date">{date_long}</div>
    </header>

    <div class="comics">
{comics_html}
    </div>
</body>
</html>
"""

COMIC_TEMPLATE = """        <div class="comic">
            <div class="comic-name">{name}</div>
            <img src="data:image/png;base64,{image_data}" alt="{name}">
        </div>"""


def generate_html(
    comics: list[Comic],
    output_path: Path,
    columns: int = 2,
    title: str = "The Funny Pages",
) -> None:
    """Generate a printable HTML page with all comics."""
    if not comics:
        print("No comics to generate HTML from!")
        return

    date_str = comics[0].date.isoformat()
    date_long = comics[0].date.strftime("%A, %B %d, %Y")

    comics_html_parts = []
    for comic in comics:
        img_b64 = base64.b64encode(comic.image_data).decode("utf-8")
        comics_html_parts.append(
            COMIC_TEMPLATE.format(image_data=img_b64, name=comic.name)
        )

    html = HTML_TEMPLATE.format(
        title=title,
        date=date_str,
        date_long=date_long,
        columns=columns,
        comics_html="\n".join(comics_html_parts),
    )

    output_path.write_text(html)
    print(f"HTML saved to: {output_path}")
