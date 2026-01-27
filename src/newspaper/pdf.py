"""PDF generation for the funny pages."""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from newspaper.comics import Comic
from newspaper.extras import (
    Joke,
    SportsData,
    Weather,
)


def generate_pdf(
    comics: list[Comic],
    output_path: Path,
    title: str = "The Funny Pages",
    weather: Weather | None = None,
    joke: Joke | None = None,
    sports: SportsData | None = None,
) -> None:
    """Generate a printable PDF with comics and extras."""
    if not comics:
        print("No comics to generate PDF from!")
        return

    # Page setup - Letter size with margins
    page_width, page_height = LETTER
    margin = 0.5 * inch
    usable_width = page_width - (2 * margin)

    # Title/header height
    header_height = 0.7 * inch
    # Space between items
    item_spacing = 0.2 * inch
    # Space for comic name label
    label_height = 0.2 * inch

    c = canvas.Canvas(str(output_path), pagesize=LETTER)
    date_str = comics[0].date.strftime("%A, %B %d, %Y")

    def draw_header(page_title: str = title):
        """Draw the page header."""
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(
            page_width / 2, page_height - margin - 0.35 * inch, page_title
        )
        c.setFont("Helvetica", 11)
        c.drawCentredString(
            page_width / 2, page_height - margin - 0.55 * inch, date_str
        )
        # Draw a line under the header
        c.setStrokeColorRGB(0.3, 0.3, 0.3)
        c.setLineWidth(1)
        line_y = page_height - margin - header_height + 0.1 * inch
        c.line(margin, line_y, page_width - margin, line_y)
        return page_height - margin - header_height

    def draw_section_header(y: float, text: str) -> float:
        """Draw a section header and return new Y position."""
        c.setFont("Helvetica-Bold", 14)
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.drawString(margin, y - 0.2 * inch, text)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.setLineWidth(0.5)
        c.line(margin, y - 0.25 * inch, page_width - margin, y - 0.25 * inch)
        return y - 0.4 * inch

    # === FRONT PAGE: Weather, Joke, Sports ===
    has_sports = sports and (
        sports.standings or sports.warriors_recent or sports.nfl_upcoming
    )
    if weather or joke or has_sports:
        current_y = draw_header(title)

        # Weather section
        if weather:
            current_y = draw_section_header(current_y, "Weather")
            c.setFont("Helvetica-Bold", 36)
            c.setFillColorRGB(0.1, 0.1, 0.1)
            c.drawString(margin, current_y - 0.4 * inch, f"{weather.temperature}°F")
            c.setFont("Helvetica", 14)
            cond_x = margin + 1.2 * inch
            c.drawString(cond_x, current_y - 0.25 * inch, weather.condition)
            c.setFont("Helvetica", 11)
            c.setFillColorRGB(0.4, 0.4, 0.4)
            c.drawString(
                margin + 1.2 * inch, current_y - 0.45 * inch,
                f"High: {weather.high}° Low: {weather.low}°"
            )
            c.drawString(margin, current_y - 0.7 * inch, weather.location)
            current_y -= 1.0 * inch

        # Joke section
        if joke:
            current_y = draw_section_header(current_y, "Joke of the Day")
            c.setFont("Helvetica-Bold", 12)
            c.setFillColorRGB(0.1, 0.1, 0.1)
            c.drawString(margin, current_y - 0.2 * inch, f"Q: {joke.question}")
            c.setFont("Helvetica", 12)
            c.drawString(margin, current_y - 0.45 * inch, f"A: {joke.answer}")
            current_y -= 0.8 * inch

        # Sports section
        if has_sports:
            current_y = draw_section_header(current_y, "Sports")

            # NFL Upcoming Games (playoffs/Super Bowl)
            if sports.nfl_upcoming:
                c.setFont("Helvetica-Bold", 11)
                c.setFillColorRGB(0.2, 0.2, 0.2)
                c.drawString(margin, current_y - 0.15 * inch, "NFL - Upcoming")
                current_y -= 0.35 * inch

                for game in sports.nfl_upcoming:
                    c.setFont("Helvetica-Bold", 10)
                    c.setFillColorRGB(0.0, 0.3, 0.6)
                    c.drawString(margin + 0.1 * inch, current_y, game.note)
                    c.setFont("Helvetica", 10)
                    c.setFillColorRGB(0.3, 0.3, 0.3)
                    matchup = f"{game.away_team} @ {game.home_team}"
                    c.drawString(margin + 1.8 * inch, current_y, matchup)
                    c.drawString(margin + 5.5 * inch, current_y, game.date)
                    current_y -= 0.2 * inch

                current_y -= 0.15 * inch

            # Baseball Countdown
            if sports.baseball_countdown:
                countdown = sports.baseball_countdown
                c.setFont("Helvetica-Bold", 11)
                c.setFillColorRGB(0.2, 0.2, 0.2)
                c.drawString(margin, current_y - 0.15 * inch, "MLB - Countdown")
                current_y -= 0.35 * inch

                c.setFont("Helvetica", 10)
                c.setFillColorRGB(0.3, 0.3, 0.3)

                if countdown.days_to_spring_training is not None:
                    days = countdown.days_to_spring_training
                    text = f"Spring Training: {days} day{'s' if days != 1 else ''}"
                    c.drawString(margin + 0.1 * inch, current_y, text)
                    current_y -= 0.2 * inch
                else:
                    st_text = "Spring Training: Now!"
                    c.drawString(margin + 0.1 * inch, current_y, st_text)
                    current_y -= 0.2 * inch

                if countdown.days_to_opening_day is not None:
                    days = countdown.days_to_opening_day
                    c.setFont("Helvetica-Bold", 10)
                    c.setFillColorRGB(0.0, 0.3, 0.6)
                    text = f"Opening Day: {days} day{'s' if days != 1 else ''}"
                    c.drawString(margin + 0.1 * inch, current_y, text)
                    current_y -= 0.2 * inch

                current_y -= 0.15 * inch

            # MLB/NFL Standings
            for standing in sports.standings:
                # Check if we need a new page
                if current_y < 2.5 * inch:
                    c.showPage()
                    current_y = draw_header("Sports")
                    current_y = draw_section_header(current_y, "Standings")

                # Division header
                c.setFont("Helvetica-Bold", 11)
                c.setFillColorRGB(0.2, 0.2, 0.2)
                league_div = f"{standing.league} - {standing.division}"
                c.drawString(margin, current_y - 0.15 * inch, league_div)
                current_y -= 0.35 * inch

                # Teams table
                c.setFont("Helvetica", 10)
                for team_name, record, gb in standing.teams:
                    # Highlight favorite team
                    if team_name == standing.favorite_team:
                        c.setFillColorRGB(0.0, 0.3, 0.6)
                        c.setFont("Helvetica-Bold", 10)
                    else:
                        c.setFillColorRGB(0.3, 0.3, 0.3)
                        c.setFont("Helvetica", 10)

                    c.drawString(margin + 0.1 * inch, current_y, team_name)
                    c.drawString(margin + 3.5 * inch, current_y, record)
                    if gb and gb != "-":
                        c.drawString(margin + 4.5 * inch, current_y, f"GB: {gb}")
                    current_y -= 0.2 * inch

                current_y -= 0.2 * inch  # Space between divisions

            # Warriors Recent Games
            if sports.warriors_recent:
                if current_y < 2.0 * inch:
                    c.showPage()
                    current_y = draw_header("Sports")
                    current_y = draw_section_header(current_y, "Basketball")

                warriors = sports.warriors_recent
                c.setFont("Helvetica-Bold", 11)
                c.setFillColorRGB(0.0, 0.3, 0.6)
                c.drawString(
                    margin, current_y - 0.15 * inch,
                    f"{warriors.team_name} ({warriors.record})"
                )
                c.setFont("Helvetica", 10)
                c.setFillColorRGB(0.3, 0.3, 0.3)
                recent_x = margin + 3.5 * inch
                c.drawString(recent_x, current_y - 0.15 * inch, "Recent Games")
                current_y -= 0.35 * inch

                for game in warriors.games:
                    result = "W" if game.won else "L"
                    loc = "vs" if game.home else "@"
                    c.setFont("Helvetica-Bold", 10)
                    if game.won:
                        c.setFillColorRGB(0.0, 0.5, 0.0)
                    else:
                        c.setFillColorRGB(0.6, 0.0, 0.0)
                    c.drawString(margin + 0.1 * inch, current_y, result)

                    c.setFont("Helvetica", 10)
                    c.setFillColorRGB(0.3, 0.3, 0.3)
                    game_info = f"{loc} {game.opponent}"
                    c.drawString(margin + 0.4 * inch, current_y, game_info)
                    score = f"{game.team_score}-{game.opponent_score}"
                    c.drawString(margin + 2.5 * inch, current_y, score)
                    c.drawString(margin + 3.5 * inch, current_y, game.date)
                    current_y -= 0.2 * inch

                current_y -= 0.2 * inch

        # Start new page for comics
        c.showPage()

    # === COMICS PAGES ===
    def get_comic_height(comic: Comic) -> float:
        """Calculate the height a comic will take when scaled to full width."""
        try:
            img = Image.open(io.BytesIO(comic.image_data))
            img_width, img_height = img.size
            scale = usable_width / img_width
            return (img_height * scale) + label_height
        except Exception:
            return 2 * inch

    current_y = draw_header("The Funny Pages")

    for comic in comics:
        comic_height = get_comic_height(comic)

        # Check if comic fits on current page
        if current_y - comic_height < margin:
            c.showPage()
            current_y = draw_header("The Funny Pages")

        # Draw the comic
        try:
            img = Image.open(io.BytesIO(comic.image_data))
            img_width, img_height = img.size

            scale = usable_width / img_width
            draw_width = usable_width
            draw_height = img_height * scale

            draw_y = current_y - label_height - draw_height

            # Draw comic name
            c.setFont("Helvetica-Bold", 10)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            c.drawString(margin, current_y - label_height + 0.05 * inch, comic.name)

            # Draw image
            img_reader = ImageReader(img)
            c.drawImage(
                img_reader, margin, draw_y, draw_width, draw_height,
                preserveAspectRatio=True,
            )

            # Draw border
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setLineWidth(0.5)
            c.rect(margin, draw_y, draw_width, draw_height)

            current_y = draw_y - item_spacing

        except Exception as e:
            print(f"  Warning: Could not add {comic.name} to PDF: {e}")
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(0.5, 0.5, 0.5)
            err_msg = f"[{comic.name} - error loading]"
            c.drawString(margin, current_y - 0.5 * inch, err_msg)
            current_y -= 1 * inch

    c.save()
    print(f"PDF saved to: {output_path}")
