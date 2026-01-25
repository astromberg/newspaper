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
            max-width: 8.5in;
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
            display: grid;
            grid-template-columns: repeat({columns}, 1fr);
            gap: 0.2in;
        }}

        .comic {{
            break-inside: avoid;
            page-break-inside: avoid;
            margin-bottom: 0.25in;
        }}

        .comic img {{
            width: 100%;
            height: auto;
            border: 1px solid #ccc;
        }}

        .comic-name {{
            font-size: 12pt;
            font-weight: bold;
            margin-bottom: 6px;
            color: #333;
        }}

        /* For single column, fit ~3 comics per page */
        .single-column .comic {{
            max-height: 3in;
            margin-bottom: 0.3in;
        }}

        .single-column .comic img {{
            max-height: 2.8in;
            width: auto;
            max-width: 100%;
        }}

        @media print {{
            body {{
                padding: 0;
                max-width: none;
            }}

            .comic img {{
                border: 1px solid #999;
            }}
        }}

        /* Adjust these to change layout */
        @media (max-width: 600px) {{
            .comics {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <div class="date">{date_long}</div>
    </header>

    <div class="comics{single_column_class}">
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

    single_column_class = " single-column" if columns == 1 else ""

    html = HTML_TEMPLATE.format(
        title=title,
        date=date_str,
        date_long=date_long,
        columns=columns,
        single_column_class=single_column_class,
        comics_html="\n".join(comics_html_parts),
    )

    output_path.write_text(html)
    print(f"HTML saved to: {output_path}")
