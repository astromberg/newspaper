"""HTML generation for the funny pages."""

from __future__ import annotations

import base64
import io
from pathlib import Path

from PIL import Image

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
            display: flex;
            flex-direction: column;
            gap: 0.2in;
        }}

        .comic {{
            break-inside: avoid;
            page-break-inside: avoid;
            margin-bottom: 0.15in;
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
        }}

        /* Size classes based on aspect ratio */
        /* Wide strips (aspect > 2.5) - full width, ~2 per page */
        .comic.size-large {{
            max-width: 100%;
        }}

        /* Medium strips (aspect 1.5-2.5) - ~3 per page */
        .comic.size-medium {{
            max-width: 100%;
        }}

        .comic.size-medium img {{
            max-height: 2.2in;
            width: auto;
            max-width: 100%;
        }}

        /* Square/panel comics (aspect < 1.5) - ~4 per page */
        .comic.size-small {{
            max-width: 60%;
        }}

        .comic.size-small img {{
            max-height: 2in;
            width: auto;
            max-width: 100%;
        }}

        @page {{
            margin: 0.4in;
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

COMIC_TEMPLATE = """        <div class="comic {size_class}">
            <div class="comic-name">{name}</div>
            <img src="data:image/png;base64,{image_data}" alt="{name}">
        </div>"""


def get_size_class(image_data: bytes) -> str:
    """Determine size class based on image aspect ratio."""
    try:
        img = Image.open(io.BytesIO(image_data))
        width, height = img.size
        aspect_ratio = width / height

        if aspect_ratio > 2.5:
            return "size-large"  # Wide strips like Sunday comics
        elif aspect_ratio > 1.5:
            return "size-medium"  # Standard daily strips
        else:
            return "size-small"  # Square panels like Far Side
    except Exception:
        return "size-medium"  # Default to medium


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

    # Calculate size class for each comic and sort by size
    # Order: large first, then medium, then small (packs better)
    size_order = {"size-large": 0, "size-medium": 1, "size-small": 2}
    comics_with_size = [
        (comic, get_size_class(comic.image_data)) for comic in comics
    ]
    comics_with_size.sort(key=lambda x: size_order[x[1]])

    comics_html_parts = []
    for comic, size_class in comics_with_size:
        img_b64 = base64.b64encode(comic.image_data).decode("utf-8")
        comics_html_parts.append(
            COMIC_TEMPLATE.format(
                image_data=img_b64, name=comic.name, size_class=size_class
            )
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
