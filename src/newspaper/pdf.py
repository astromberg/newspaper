"""PDF generation for the funny pages."""

import io
from pathlib import Path

from PIL import Image
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from newspaper.comics import Comic


def generate_pdf(
    comics: list[Comic], output_path: Path, title: str = "The Funny Pages"
) -> None:
    """Generate a printable PDF with all comics arranged on the page."""
    if not comics:
        print("No comics to generate PDF from!")
        return

    # Page setup - Letter size with margins
    page_width, page_height = LETTER
    margin = 0.5 * inch
    usable_width = page_width - (2 * margin)
    usable_height = page_height - (2 * margin)

    # Title area
    title_height = 0.6 * inch
    content_height = usable_height - title_height

    # Calculate grid layout (2 columns)
    cols = 2
    rows = (len(comics) + 1) // 2  # Ceiling division

    cell_width = usable_width / cols
    cell_height = content_height / rows
    padding = 0.1 * inch

    c = canvas.Canvas(str(output_path), pagesize=LETTER)

    # Draw title
    date_str = comics[0].date.strftime("%A, %B %d, %Y")
    c.setFont("Helvetica-Bold", 24)
    title_y = page_height - margin - 0.4 * inch
    c.drawCentredString(page_width / 2, title_y, title)
    c.setFont("Helvetica", 12)
    c.drawCentredString(page_width / 2, page_height - margin - 0.55 * inch, date_str)

    # Draw each comic
    for i, comic in enumerate(comics):
        row = i // cols
        col = i % cols

        # Cell position (from top-left)
        cell_x = margin + (col * cell_width)
        cell_y = page_height - margin - title_height - ((row + 1) * cell_height)

        # Load and scale image
        try:
            img = Image.open(io.BytesIO(comic.image_data))

            # Calculate scaling to fit in cell (with padding)
            available_width = cell_width - (2 * padding)
            # Leave space for label below
            available_height = cell_height - (2 * padding) - 0.2 * inch

            img_width, img_height = img.size
            scale = min(available_width / img_width, available_height / img_height)

            draw_width = img_width * scale
            draw_height = img_height * scale

            # Center in cell
            draw_x = cell_x + padding + (available_width - draw_width) / 2
            label_offset = 0.2 * inch
            v_offset = (available_height - draw_height) / 2
            draw_y = cell_y + padding + label_offset + v_offset

            # Draw comic name
            c.setFont("Helvetica-Bold", 9)
            c.drawString(cell_x + padding, cell_y + padding, comic.name)

            # Draw image
            img_reader = ImageReader(img)
            c.drawImage(img_reader, draw_x, draw_y, draw_width, draw_height)

        except Exception as e:
            print(f"  Warning: Could not add {comic.name} to PDF: {e}")
            # Draw placeholder
            c.setFont("Helvetica", 10)
            err_msg = f"[{comic.name} - error loading]"
            c.drawString(cell_x + padding, cell_y + cell_height / 2, err_msg)

    c.save()
    print(f"PDF saved to: {output_path}")
