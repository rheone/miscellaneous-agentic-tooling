"""Font anatomy: what each Pixoo font really draws, measured with the integration's own code.

Coordinates: every row number is relative to the `y` of the text component.
Row 0 is the row the integration aligns the top of a capital letter to (the cap line).
Negative rows are drawn ABOVE `y` (accents, i-dots in some BDF fonts).
Every column number is relative to the pen position of the glyph.
"""
from __future__ import annotations

import string
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

CANVAS = 64

# Glyph status values. "ok" and "case" draw what the reader expects (case = upper-case shape).
OK, CASE, TYPO, MISSING, BLANK = "ok", "case-fallback", "typography-fallback", "missing", "blank"
STATUS_HELP = {
    OK: "drawn from its own glyph",
    CASE: "no glyph of its own; drawn with the upper-case glyph",
    TYPO: "no glyph of its own; drawn with a plain ASCII stand-in (curly quote -> straight, dash -> '-')",
    MISSING: "not in the font",
    BLANK: "the font has the code point, but the glyph is empty: it draws a gap, no pixels",
}


class _Recorder:
    """Mock Pixoo that records where pixels land."""

    def __init__(self):
        self.points: List[Tuple[int, int]] = []

    def draw_pixel(self, xy, rgb=None):
        self.points.append((int(xy[0]), int(xy[1])))


@dataclass
class Glyph:
    char: str
    status: str
    drawn_as: Optional[str]  # the glyph actually drawn ('?' for missing BDF chars), None = nothing
    advance: int             # how far the pen moves when drawing
    width_counted: int       # what the width calculation adds (differs from advance for missing matrix chars)
    ink: Optional[Tuple[int, int, int, int]]  # x0, y0, x1, y1 relative to pen / component y; None = no pixels
    pixels: List[Tuple[int, int]] = field(default_factory=list)

    @property
    def problem(self) -> bool:
        return self.status in (MISSING, BLANK)


def is_bdf(font) -> bool:
    return hasattr(font, "glyphs") and hasattr(font, "baseline_offset")


def glyph(src, font, ch: str) -> Glyph:
    """Analyse one character exactly as the integration will draw it."""
    rec = _Recorder()
    advance = font.draw_character(rec, ch, (0, 0), (255, 255, 255)) or 0
    pts = rec.points
    ink = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)) if pts else None
    width_counted = font.get_text_width(ch + "0") - font.get_text_width("0")
    fallbacks = src.bdf.TYPOGRAPHY_FALLBACKS
    if ch == " ":
        return Glyph(ch, OK, " ", advance, width_counted, None, [])
    if is_bdf(font):
        table = font.glyphs
        if ch in table:
            status, drawn = (OK if pts else BLANK), ch
        elif ch in fallbacks and fallbacks[ch] in table:
            status, drawn = TYPO, fallbacks[ch]
        elif ch.upper() in table:
            status, drawn = CASE, ch.upper()
        else:
            status, drawn = MISSING, ("?" if "?" in table else None)
    else:
        table = font.raw_dict
        if ch in table:
            status, drawn = (OK if pts or ch.isspace() else BLANK), ch
        elif ch in fallbacks and fallbacks[ch] in table:
            status, drawn = TYPO, fallbacks[ch]
        elif ch.upper() in table:
            status, drawn = CASE, ch.upper()
        else:
            status, drawn = MISSING, None
    if status in (CASE, TYPO) and not pts and not ch.isspace():
        status = BLANK  # the stand-in glyph is itself empty (PICO_8: 'é' -> blank 'É')
    return Glyph(ch, status, drawn, advance, width_counted, ink, pts)


def _ink_rows(src, font, chars: str) -> Optional[Tuple[int, int]]:
    tops, bottoms = [], []
    for c in chars:
        g = glyph(src, font, c)
        if g.status == OK and g.ink:
            tops.append(g.ink[1])
            bottoms.append(g.ink[3])
    return (min(tops), max(bottoms)) if tops else None


@dataclass
class FontInfo:
    key: str                 # what to write in YAML `font:`
    name: str                # display / file name
    kind: str                # "bdf" or "matrix"
    origin: str              # "bundled", "built-in", "user" (/config/fonts) or "esphome"
    path: Optional[str]
    line_height: int         # y step between lines of one text component
    cap_top: int             # first row of a capital / digit (0 for every bundled font)
    baseline: int            # last row of a capital / digit
    cap_height: int
    x_height: Optional[int]  # height of 'x' when it differs from caps
    descender: int           # rows below the baseline used by g j p q y
    ink_top_ascii: int       # highest row any printable ASCII glyph reaches (negative = above y)
    ink_bottom_ascii: int
    ink_top_any: int         # same over every glyph in the font (accented capitals reach higher)
    ink_bottom_any: int
    lowercase: str           # "true", "small-caps", "same as capitals", "upper-case fallback" or "none (no letters)"
    monospace: bool
    tabular_digits: bool
    digit_advance: Tuple[int, int]
    space_advance: int
    tracking: str
    glyph_count: int
    blank_count: int
    ascii_missing: str
    per_line: Dict[str, int]
    coverage: Dict[str, int]
    notes: List[str]

    def as_dict(self):
        return dict(self.__dict__)


def _origin(src, path: Optional[str]) -> str:
    if not path:
        return "built-in"
    p = path.replace("\\", "/")
    if "/esphome/fonts/" in p:
        return "esphome"
    if p.startswith(src.integration_dir.replace("\\", "/")):
        return "bundled"
    return "user"


def capacity(font, ch: str, width: int = CANVAS, src=None) -> int:
    """How many copies of `ch` fit in `width` px (0 when the font cannot draw `ch`)."""
    if src is not None and glyph(src, font, ch).status in (MISSING, BLANK):
        return 0
    n = 0
    while font.get_text_width(ch * (n + 1)) <= width:
        n += 1
        if n > 200:
            break
    return n


def font_keys(src) -> List[str]:
    """Every name a YAML `font:` can resolve to (lower case, without the `font_` alias)."""
    m = src.manager
    keys = {k for k in m._fonts if not k.startswith("font_")} | set(m._available_bdf_files)
    return sorted(keys)


def get(src, key: str):
    """Resolve a YAML font name like the integration (no silent fallback here: None when unknown)."""
    return src.manager.get_font(key, fallback=False)


def resolve(src, key) -> Tuple[object, bool]:
    """Resolve like the integration does at render time. Returns (font, fell_back_to_pico_8)."""
    f = src.manager.get_font(key, fallback=False) if isinstance(key, str) and key.strip() else None
    if f is None:
        return src.manager.get_font("pico_8", fallback=False), bool(isinstance(key, str) and key.strip())
    return f, False


def _coverage(src, font) -> Tuple[Dict[str, int], int, int]:
    classes = {
        "digits": "0123456789", "upper": string.ascii_uppercase, "lower": string.ascii_lowercase,
        "ascii_punct": string.punctuation,
    }
    cov = {}
    for name, chars in classes.items():
        cov[name] = sum(1 for c in chars if glyph(src, font, c).status in (OK,))
    if is_bdf(font):
        table = font.glyphs
        blank = sum(1 for c, g in table.items() if c.strip() and not any("1" in r for r in g["bitmap"]))
        drawable = [c for c, g in table.items() if any("1" in r for r in g["bitmap"])]
        buckets = {"latin_accented": (0x00C0, 0x024F), "greek": (0x0370, 0x03FF), "cyrillic": (0x0400, 0x04FF),
                   "arrows": (0x2190, 0x21FF), "box_and_blocks": (0x2500, 0x259F), "symbols": (0x2600, 0x27BF)}
        for name, (lo, hi) in buckets.items():
            cov[name] = sum(1 for c in drawable if lo <= ord(c) <= hi)
        return cov, len(table), blank
    table = font.raw_dict
    return cov, len(table), 0


def info(src, key: str) -> FontInfo:
    f = get(src, key)
    if f is None:
        raise KeyError(key)
    bdf = is_bdf(f)
    caps = _ink_rows(src, f, "HEFT0") or _ink_rows(src, f, "0") or (0, 0)
    asc = _ink_rows(src, f, "".join(chr(o) for o in range(33, 127))) or caps
    if bdf:
        every = [g for g in (glyph(src, f, c) for c in f.glyphs if c.strip()) if g.ink]
        any_top, any_bottom = min(g.ink[1] for g in every), max(g.ink[3] for g in every)
    else:
        any_top, any_bottom = asc
    desc_rows = _ink_rows(src, f, "gjpqy")
    descender = max(0, desc_rows[1] - caps[1]) if desc_rows else 0
    lower_status = [glyph(src, f, c).status for c in string.ascii_lowercase]
    xr = _ink_rows(src, f, "xvwz")
    if OK not in lower_status:
        upper_ok = sum(1 for c in string.ascii_uppercase if glyph(src, f, c).status == OK)
        lowercase = "upper-case fallback" if upper_ok >= 20 else "none (no letters)"
        x_height = None
    elif all(glyph(src, f, c).pixels == glyph(src, f, c.upper()).pixels for c in string.ascii_lowercase
             if glyph(src, f, c).status == OK):
        lowercase, x_height = "same as capitals", None  # five_pix: lower-case glyphs are copies of the capitals
    else:
        tall = _ink_rows(src, f, "bdhkl")
        x_height = (xr[1] - xr[0] + 1) if xr else None
        if x_height == caps[1] - caps[0] + 1:
            x_height = None
        lowercase = "small-caps" if tall and xr and tall[0] == xr[0] and x_height else "true"
    printable = [c for c in (chr(o) for o in range(33, 127)) if glyph(src, f, c).status == OK]
    advances = {glyph(src, f, c).advance for c in printable}
    digit_adv = [glyph(src, f, c).advance for c in "0123456789" if glyph(src, f, c).status == OK]
    cov, count, blank = _coverage(src, f)
    missing = "".join(c for c in (chr(o) for o in range(32, 127)) if glyph(src, f, c).status in (MISSING, BLANK))
    lh = f.get_line_height()
    notes = []
    ink_span = asc[1] - min(asc[0], 0) + 1
    if lh <= ink_span:
        notes.append(f"line height {lh} leaves no blank row between lines (ASCII ink spans {ink_span} rows)")
    if asc[0] < 0:
        notes.append(f"some ASCII glyphs draw {-asc[0]} row(s) above y; keep y >= {-asc[0]} at the top edge")
    if any_top < asc[0]:
        notes.append(f"accented capitals reach row {any_top}; keep y >= {-any_top} if the text may hold them")
    if blank:
        notes.append(f"{blank} code points have empty glyphs and draw a gap (check with `coverage`)")
    if digit_adv and len(set(digit_adv)) > 1:
        notes.append("digits differ in width: a changing number shifts sideways; right-align it or use a tabular font")
    if lowercase == "same as capitals":
        notes.append("lower-case glyphs exist but are copies of the capitals: lower case looks like capitals")
    if lowercase == "upper-case fallback":
        notes.append("no lower case: lower-case input is drawn with the capital glyphs")
    if lowercase == "small-caps":
        notes.append("lower case is drawn as small capitals (shorter capitals, no ascenders or descenders)")
    if not bdf:
        notes.append("missing characters draw nothing, but still add 1 px to the measured width, which shifts centered text")
    else:
        notes.append("missing characters draw '?' in this font")
    if bdf and printable:
        first = glyph(src, f, "H") if glyph(src, f, "H").ink else None
        if first and first.ink[0] > 0:
            notes.append(f"glyphs start {first.ink[0]} px right of the pen (left side bearing); left-aligned ink begins at x+{first.ink[0]}")
    return FontInfo(
        key=key, name=getattr(f, "name", key), kind="bdf" if bdf else "matrix",
        origin=_origin(src, getattr(f, "file_path", None) if bdf else None),
        path=getattr(f, "file_path", None) if bdf else None,
        line_height=lh, cap_top=caps[0], baseline=caps[1], cap_height=caps[1] - caps[0] + 1,
        x_height=x_height, descender=descender,
        ink_top_ascii=asc[0], ink_bottom_ascii=asc[1], ink_top_any=any_top, ink_bottom_any=any_bottom,
        lowercase=lowercase, monospace=len(advances) == 1, tabular_digits=len(set(digit_adv)) == 1,
        digit_advance=(min(digit_adv), max(digit_adv)) if digit_adv else (0, 0),
        space_advance=glyph(src, f, " ").advance,
        tracking=("each glyph's own advance (spacing is built into the glyph)" if bdf
                  else "glyph width + 1 px between characters"),
        glyph_count=count, blank_count=blank, ascii_missing=missing,
        per_line={c: capacity(f, c, CANVAS, src) for c in ("0", "A", "a", "M", "i")},
        coverage=cov, notes=notes,
    )


def all_info(src) -> List[FontInfo]:
    return [info(src, k) for k in font_keys(src)]


def char_name(ch: str) -> str:
    if ch == "\n":
        return "LINE FEED"
    return unicodedata.name(ch, f"U+{ord(ch):04X}")
