#!/usr/bin/env python3
"""Draw a one-page newspaper poster summing up the world news of
Saturday 21 November 2026 and write it to /output/entry.png.

Runs with no network. Uses Pillow when it is available and falls back
to a pure standard-library renderer otherwise, so it works in the
judge's standard-library-only sandbox. Output is deterministic: the
same bytes on every run.
"""

import os
import struct
import sys
import zlib

SIZE = 1024
OUT_NAME = "entry.png"

PAPER = (247, 243, 234)
INK = (20, 26, 40)
NAVY = (18, 38, 76)
NAVY_LIGHT = (216, 222, 233)
RED = (178, 34, 34)
GOLD = (201, 168, 106)
GREY = (92, 97, 108)
LINE = (205, 198, 184)
WHITE = (255, 255, 255)

# (tag, accent colour, headline, body) — all reported on 21 Nov 2026.
STORIES = [
    (
        "CONFLICT",
        (178, 34, 34),
        "Russian missiles land in Poland",
        "Two Russian missiles and a suspected drone came down in "
        "south-east Poland during a huge overnight attack on Ukraine. "
        "PM Tusk called it a provocation; NATO chief Rutte, a grave "
        "violation. No one was hurt.",
    ),
    (
        "DIPLOMACY",
        (18, 38, 76),
        "Trump, Xi and Putin summit ends thin",
        "The first US-China-Russia summit in Shenzhen ended thin. "
        "Trump said Putin wants diplomacy, and the US seeks a "
        "Ukraine deal by January.",
    ),
    (
        "MARKETS",
        (27, 94, 60),
        "Wall Street slides into correction",
        "The S&P 500 and the Dow entered correction as AI shares "
        "sold off. The Nasdaq fell 5.28% and Nvidia dropped about 14%.",
    ),
    (
        "EUROPE",
        (96, 48, 120),
        "Denmark expels Russian diplomat",
        "Copenhagen expelled Russia's defence attache, accusing "
        "Moscow of plotting to kill a Ukrainian rapper at a concert "
        "near the capital.",
    ),
    (
        "WEATHER",
        (14, 110, 130),
        "Cyclone Akvan weakens after landfall",
        "The storm crossed India's Odisha coast near Gopalpur with "
        "winds gusting to 90 km/h. Over 300,000 people were moved "
        "to shelters.",
    ),
    (
        "JUSTICE",
        (120, 74, 10),
        "Palisades Fire arson verdict",
        "A Los Angeles jury convicted Jonathan Rinderknecht of "
        "starting the Palisades Fire, from the January 2025 wildfires.",
    ),
    (
        "MIDDLE EAST",
        (140, 60, 20),
        "Houthi missiles intercepted over Riyadh",
        "The Saudi-led coalition said it destroyed three Houthi "
        "ballistic missiles fired at Riyadh and struck Hodeidah "
        "in response.",
    ),
]

FOOTER_LINE_1 = "Reported 21 November 2026  |  Sources: AP, Reuters, Al Jazeera, IMD"
FOOTER_LINE_2 = "Drawn by a program, no network used"


def output_path():
    base = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, OUT_NAME)


# ---------------------------------------------------------------- PIL path

def _font(path, size):
    from PIL import ImageFont

    for candidate in (path,):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_with_pillow(path):
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(img)
    font_dir = "/usr/share/fonts/truetype/dejavu"
    bold = os.path.join(font_dir, "DejaVuSans-Bold.ttf")
    regular = os.path.join(font_dir, "DejaVuSans.ttf")

    f_kicker = _font(bold, 24)
    f_title = _font(bold, 54)
    f_sub = _font(regular, 22)
    f_tag = _font(bold, 18)
    f_tag_small = _font(bold, 16)
    f_head = _font(bold, 33)
    f_head_small = _font(bold, 27)
    f_body = _font(regular, 20)
    f_body_small = _font(regular, 18)
    f_foot = _font(regular, 15)

    # Masthead.
    draw.rectangle([0, 0, SIZE, 158], fill=NAVY)
    draw.text((48, 26), "T H E   W O R L D   I N   O N E   D A Y",
              font=f_kicker, fill=GOLD)
    draw.text((48, 58), "Saturday, 21 November 2026",
              font=f_title, fill=WHITE)
    draw.text((48, 122), "Seven stories from around the globe, as reported today",
              font=f_sub, fill=NAVY_LIGHT)
    draw.rectangle([0, 158, SIZE, 164], fill=RED)

    text_x = 108
    text_w = SIZE - 48 - text_x
    y = 176
    for index, (tag, accent, headline, body) in enumerate(STORIES):
        top = index == 0
        block_h = 170 if top else 104
        # Number badge.
        cx, cy, r = 64, y + (30 if top else 24), 23
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent)
        num = str(index + 1)
        nw = draw.textlength(num, font=_font(bold, 24))
        draw.text((cx - nw / 2, cy - 15), num, font=_font(bold, 24),
                  fill=WHITE)
        # Tag, headline, body.
        draw.text((text_x, y), tag, font=f_tag if top else f_tag_small,
                  fill=accent)
        hy = y + (26 if top else 22)
        draw.text((text_x, hy), headline,
                  font=f_head if top else f_head_small, fill=INK)
        by = hy + (44 if top else 36)
        body_font = f_body if top else f_body_small
        lines = _wrap(draw, body, body_font, text_w)
        for line in lines[:3 if top else 2]:
            draw.text((text_x, by), line, font=body_font, fill=(52, 58, 70))
            by += 26 if top else 23
        y += block_h
        if index < len(STORIES) - 1:
            draw.line([(40, y - 2), (SIZE - 40, y - 2)], fill=LINE, width=1)

    draw.text((SIZE / 2, 980), FOOTER_LINE_1, font=f_foot, fill=GREY,
              anchor="mt")
    draw.text((SIZE / 2, 1000), FOOTER_LINE_2, font=f_foot, fill=GREY,
              anchor="mt")
    img.save(path, format="PNG", optimize=True)


# ------------------------------------------------------- stdlib fallback

# 5x7 bitmap glyphs, each row a 5-bit integer, for the fallback renderer.
GLYPHS = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0, 0x04, 0x04, 0x0E, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    "|": (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
}


def _clean(text):
    return (text.upper()
            .replace("\u2014", "-").replace("\u2013", "-")
            .replace("\u00b7", "-").replace("\u2019", "'"))


def _wrap_plain(text, max_chars):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if len(trial) <= max_chars:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Canvas:
    def __init__(self):
        self.pixels = bytearray(PAPER * SIZE * SIZE)

    def rect(self, x0, y0, x1, y1, colour):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(SIZE, x1)
        y1 = min(SIZE, y1)
        row = bytes(colour) * (x1 - x0)
        for y in range(y0, y1):
            start = (y * SIZE + x0) * 3
            self.pixels[start:start + len(row)] = row

    def text(self, x, y, raw, scale, colour):
        text = _clean(raw)
        cursor = x
        for char in text:
            glyph = GLYPHS.get(char, GLYPHS[" "])
            for row_i, bits in enumerate(glyph):
                for col_i in range(5):
                    if bits & (1 << (4 - col_i)):
                        px = cursor + col_i * scale
                        py = y + row_i * scale
                        self.rect(px, py, px + scale, py + scale, colour)
            cursor += 6 * scale
        return cursor


def _png_chunk(kind, data):
    chunk = struct.pack(">I", len(data)) + kind + data
    chunk += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return chunk


def draw_with_stdlib(path):
    canvas = Canvas()
    canvas.rect(0, 0, SIZE, 158, NAVY)
    canvas.text(48, 30, "THE WORLD IN ONE DAY", 3, GOLD)
    canvas.text(48, 66, "SATURDAY, 21 NOVEMBER 2026", 4, WHITE)
    canvas.text(48, 122, "SEVEN STORIES FROM AROUND THE GLOBE, AS REPORTED TODAY",
                2, NAVY_LIGHT)
    canvas.rect(0, 158, SIZE, 164, RED)

    text_x = 108
    body_chars = (SIZE - 48 - text_x) // 12
    y = 176
    for index, (tag, accent, headline, body) in enumerate(STORIES):
        top = index == 0
        block_h = 170 if top else 104
        canvas.rect(40, y + 6, 88, y + 54, accent)
        canvas.text(56, y + 16, str(index + 1), 3, WHITE)
        canvas.text(text_x, y, tag, 2, accent)
        canvas.text(text_x, y + 26, headline, 3 if top else 2, INK)
        lines = _wrap_plain(_clean(body), body_chars)
        line_y = y + (26 + 30 if top else 26 + 24)
        for line in lines[:3 if top else 2]:
            canvas.text(text_x, line_y, line, 2, (52, 58, 70))
            line_y += 24
        y += block_h
        if index < len(STORIES) - 1:
            canvas.rect(40, y - 2, SIZE - 40, y - 1, LINE)

    footer1 = _clean(FOOTER_LINE_1)
    fw1 = len(footer1) * 12
    canvas.text((SIZE - fw1) // 2, 980, footer1, 2, GREY)
    footer2 = _clean(FOOTER_LINE_2)
    fw2 = len(footer2) * 12
    canvas.text((SIZE - fw2) // 2, 1000, footer2, 2, GREY)

    raw = bytearray()
    for row_i in range(SIZE):
        raw.append(0)
        start = row_i * SIZE * 3
        raw += canvas.pixels[start:start + SIZE * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0))
    png += _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _png_chunk(b"IEND", b"")
    with open(path, "wb") as handle:
        handle.write(png)


def main():
    path = output_path()
    try:
        import PIL  # noqa: F401
    except ImportError:
        draw_with_stdlib(path)
    else:
        draw_with_pillow(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
