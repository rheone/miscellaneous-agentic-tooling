"""Measure, wrap and place text the way divoom_pixoo 1.24.0 draws it, and suggest fonts for a box."""
from __future__ import annotations

import re
import string
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from . import fonts as F

CANVAS = 64
ALIGNS = ("left", "center", "right")


class Recorder:
    """Mock Pixoo canvas: records every pixel, including those that fall off the 64x64 grid."""

    def __init__(self):
        self.points: List[Tuple[int, int]] = []

    def draw_pixel(self, xy, rgb=None):
        self.points.append((int(xy[0]), int(xy[1])))


@dataclass
class Line:
    text: str
    width: int                       # what the integration measures (used for alignment)
    start_x: int                     # pen x of the first glyph
    ink: Optional[Tuple[int, int, int, int]]


@dataclass
class Measurement:
    font_requested: str
    font: str
    fell_back: bool
    text: str
    x: int
    y: int
    align: str
    line_height: int
    lines: List[Line]
    ink: Optional[Tuple[int, int, int, int]]          # absolute x0, y0, x1, y1
    pixels: List[Tuple[int, int]]
    glyph_issues: List[F.Glyph]
    off_canvas: int
    issues: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)

    @property
    def fits(self) -> bool:
        return (self.off_canvas == 0 and not self.fell_back and not any(g.problem for g in self.glyph_issues)
                and not any(i.startswith(("not in ", "empty glyph")) for i in self.issues))

    def as_dict(self):
        return {
            "font": self.font, "font_requested": self.font_requested, "fell_back_to_pico_8": self.fell_back,
            "text": self.text, "position": [self.x, self.y], "align": self.align,
            "line_height": self.line_height,
            "lines": [{"text": l.text, "width": l.width, "start_x": l.start_x, "ink": l.ink} for l in self.lines],
            "ink": self.ink, "off_canvas_pixels": self.off_canvas,
            "glyphs": [{"char": g.char, "name": F.char_name(g.char), "status": g.status, "drawn_as": g.drawn_as}
                       for g in self.glyph_issues],
            "issues": self.issues, "hints": self.hints, "fits": self.fits,
        }


def _bbox(points):
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def _start_x(font, line: str, x: int, align: str) -> int:
    width = font.get_text_width(line)
    if align == "center":
        return x + int(width / 2) * -1
    if align == "right":
        return x - width
    return x


def glyph_report(src, font, text: str) -> List[F.Glyph]:
    """One entry per distinct character that is not drawn from its own glyph."""
    seen, out = set(), []
    for ch in text:
        if ch in seen or ch == "\n":
            continue
        seen.add(ch)
        g = F.glyph(src, font, ch)
        if g.status != F.OK:
            out.append(g)
    return out


def measure(src, font_name, text: str, x: int = 0, y: int = 0, align: str = "left") -> Measurement:
    """Draw `text` on a mock canvas exactly like a `text` component and report what happened."""
    font, fell_back = F.resolve(src, font_name)
    text = str(text)
    align_eff = (align or "").lower()
    rec = Recorder()
    font.draw_text(rec, text, (x, y), (255, 255, 255), align_eff if align_eff in ALIGNS else "left")
    lines, lh = [], font.get_line_height()
    for i, raw in enumerate(text.split("\n")):
        sx = _start_x(font, raw, x, align_eff)
        one = Recorder()
        font.draw_text(one, raw, (x, y + i * lh), (255, 255, 255), align_eff if align_eff in ALIGNS else "left")
        lines.append(Line(raw, font.get_text_width(raw), sx, _bbox(one.points)))
    off = sum(1 for (px, py) in rec.points if not (0 <= px < CANVAS and 0 <= py < CANVAS))
    key = getattr(font, "name", "pico_8").lower()
    m = Measurement(str(font_name), key, fell_back, text, x, y, align_eff or "left", lh, lines,
                    _bbox(rec.points), rec.points, glyph_report(src, font, text), off)
    _annotate(src, font, m, align)
    return m


def _annotate(src, font, m: Measurement, align_raw: str):
    if m.fell_back:
        m.issues.append(f"unknown font '{m.font_requested}': the integration logs a warning and draws with pico_8")
    if align_raw and align_raw.lower() not in ALIGNS:
        m.issues.append(f"align '{align_raw}' is not left/center/right: the text is drawn left-aligned")
    marks = sorted({c for c in m.text if unicodedata.combining(c)})
    if marks:
        m.issues.append("not in " + m.font + ": combining mark(s) " + ", ".join(F.char_name(c).lower() for c in marks)
                        + "; the integration draws each as a separate glyph, beside the letter. "
                        + "Use precomposed text (NFC): '" + unicodedata.normalize("NFC", m.text).replace("\n", "\\n") + "'")
    missing = [g for g in m.glyph_issues if g.status == F.MISSING]
    blank = [g for g in m.glyph_issues if g.status == F.BLANK]
    if missing:
        what = "draws '?' for each" if F.is_bdf(font) and missing[0].drawn_as == "?" else \
            "draws nothing for each but still adds 1 px to the width used for alignment"
        names = ", ".join(f"'{g.char}' {F.char_name(g.char).lower()}" for g in missing)
        m.issues.append(f"not in {m.font}: {names}; it {what}")
    if blank:
        names = ", ".join(f"'{g.char}' {F.char_name(g.char).lower()}" for g in blank)
        m.issues.append(f"empty glyph in {m.font}: {names}; each draws a gap")
    for g in m.glyph_issues:
        if g.status == F.CASE:
            m.hints.append(f"'{g.char}' is drawn with the capital '{g.drawn_as}' ({m.font} has no lower case for it)")
        elif g.status == F.TYPO:
            m.hints.append(f"'{g.char}' ({F.char_name(g.char).lower()}) is drawn as '{g.drawn_as}'")
    if m.ink:
        x0, y0, x1, y1 = m.ink
        if m.off_canvas:
            sides = [s for s, bad in (("left", x0 < 0), ("right", x1 >= CANVAS), ("top", y0 < 0),
                                      ("bottom", y1 >= CANVAS)) if bad]
            widest = max(l.width for l in m.lines)
            m.issues.append(f"{m.off_canvas} px fall off the display ({', '.join(sides)}); widest line {widest} px")
        if y0 < m.y:
            m.hints.append(f"ink starts {m.y - y0} row(s) above y={m.y} (accents or i-dots); "
                           f"the visual top is row {y0}")
        if m.align == "right" and x1 < m.x - 1:
            gap = m.x - x1
            m.hints.append(f"right-aligned ink ends at column {x1}, {gap} px left of x (the last glyph's advance "
                           f"includes trailing space); to end the ink at column C use x = C + {gap}, "
                           f"e.g. x={63 + gap} for the right edge")
        if m.align == "center" and 0 <= x0 and x1 < CANVAS:
            left, right = x0, CANVAS - 1 - x1
            if abs(left - right) >= 2 and len(m.lines) == 1:
                shift = (right - left) // 2
                m.hints.append(f"margins left {left} px, right {right} px: x={m.x + shift} centers the ink")


# ---------------------------------------------------------------- wrapping

def _greedy(font, words: Sequence[str], width: int) -> Optional[List[str]]:
    lines: List[str] = []
    cur = ""
    for w in words:
        if font.get_text_width(w) > width:
            return None
        trial = w if not cur else cur + " " + w
        if font.get_text_width(trial) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _hyphenate(font, words: Sequence[str], width: int) -> List[str]:
    out: List[str] = []
    for w in words:
        while font.get_text_width(w) > width and len(w) > 3:
            cut = len(w) - 1
            while cut > 2 and font.get_text_width(w[:cut] + "-") > width:
                cut -= 1
            if cut <= 2:
                break
            out.append(w[:cut] + "-")
            w = w[cut:]
        out.append(w)
    return out


def wrap(src, font_name, text: str, max_width: int = 62, max_lines: Optional[int] = None,
         keep_breaks: bool = False, hyphenate: bool = False) -> Optional[List[str]]:
    """Fewest lines first, then the narrowest (most even) wrap. None when no wrap fits."""
    font, _ = F.resolve(src, font_name)
    paragraphs = str(text).split("\n") if keep_breaks else [str(text).replace("\n", " ")]
    result: List[str] = []
    for para in paragraphs:
        words = para.split()
        if not words:
            result.append("")
            continue
        if hyphenate:
            words = _hyphenate(font, words, max_width)
        lines = _greedy(font, words, max_width)
        if lines is None:
            return None
        k = len(lines)
        lo = max(font.get_text_width(w) for w in words)
        hi = max_width
        while lo < hi:  # narrowest width that keeps the same number of lines
            mid = (lo + hi) // 2
            trial = _greedy(font, words, mid)
            if trial is not None and len(trial) <= k:
                hi = mid
            else:
                lo = mid + 1
        result.extend(_greedy(font, words, lo) or lines)
    if max_lines is not None and len(result) > max_lines:
        return None
    return result


# ---------------------------------------------------------------- suggestion

ROLES = ("auto", "headline", "body", "value", "label", "time")
_NUMERIC = re.compile(r"^[\s0-9.,:%°+\-/]*[A-Za-z°%]{0,3}$")


def guess_role(text: str) -> str:
    t = text.strip()
    if re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", t):
        return "time"
    if t and _NUMERIC.match(t) and any(c.isdigit() for c in t):
        return "value"
    return "headline" if len(t) <= 12 else "body"


@dataclass
class Candidate:
    font: str
    lines: List[str]
    position: Tuple[int, int]
    align: str
    ink: Tuple[int, int, int, int]
    cap_height: int
    score: float
    reasons: List[str]
    measurement: Measurement

    def component(self, color="white") -> Dict:
        return {"type": "text", "content": "\n".join(self.lines), "font": self.font, "color": color,
                "align": self.align, "position": list(self.position)}


@dataclass
class Rejection:
    font: str
    reason: str


def _score(info: F.FontInfo, role: str, text: str, lines: List[str], status: List[str]) -> Tuple[float, List[str]]:
    reasons: List[str] = []
    cap = info.cap_height
    has_lower = any(c.islower() for c in text)
    has_digit = any(c.isdigit() for c in text)
    n = len(lines)
    if role in ("headline", "value", "time"):
        score = cap * 3.0 - (n - 1) * 4.0
        reasons.append(f"{cap} px capitals" + (f", {n} lines" if n > 1 else ""))
    elif role == "label":
        score = 20.0 - cap * 2.0 - (n - 1) * 3.0
        reasons.append(f"compact {cap} px capitals")
    else:  # body
        score = 20.0 - abs(cap - 6) * 2.0 - (n - 1) * 1.0
        reasons.append(f"{cap} px capitals, {n} line(s)")
    if has_lower:
        if info.lowercase == "true":
            score += 2.0
            reasons.append("real lower case")
        elif info.lowercase == "small-caps":
            score -= 0.5
            reasons.append("lower case shown as small capitals")
        else:
            score -= 1.0
            reasons.append("lower case shown as capitals")
    if has_digit and role in ("value", "time"):
        if info.tabular_digits:
            score += 3.0
            reasons.append("all digits the same width (no jitter when the value changes)")
        else:
            score -= 2.0
            reasons.append("digits differ in width (value shifts as it changes)")
    if F.TYPO in status:
        reasons.append("some typography drawn as ASCII stand-ins")
    if info.line_height <= info.ink_bottom_ascii - min(0, info.ink_top_ascii) + 1 and n > 1:
        score -= 3.0
        reasons.append("lines touch (no gap between rows of text)")
    if info.origin in ("user", "esphome"):
        reasons.append(f"{info.origin} font")
    return score, reasons


def _place(src, key, lines, box, align, valign, stable, info: F.FontInfo, margin: int):
    bx, by, bw, bh = box
    text = "\n".join(lines)
    probe = measure(src, key, text, 0, 0, "left")
    if not probe.ink:
        return "draws no pixels"
    lh = probe.line_height
    if stable:  # font-wide ASCII extents (and this sample's), so templated content does not move the block
        top = min(info.ink_top_ascii, 0, probe.ink[1])
        bottom = max((len(lines) - 1) * lh + info.ink_bottom_ascii, probe.ink[3])
    else:
        top, bottom = probe.ink[1], probe.ink[3]
    ink_h = bottom - top + 1
    if ink_h > bh:
        return f"{len(lines)} line(s) need {ink_h} rows of ink (rows {top}..{bottom} from y), the box has {bh}"
    if valign == "top":
        y = by - top
    elif valign == "bottom":
        y = by + bh - 1 - bottom
    else:
        y = by + (bh - ink_h) // 2 - top
    best = None
    lo, hi = bx + margin, bx + bw - 1 - margin
    for x in range(bx - 8, bx + bw + 8):
        m = measure(src, key, text, x, y, align)
        if not m.ink or m.off_canvas:
            continue
        x0, _, x1, _ = m.ink
        if x0 < lo or x1 > hi:
            continue
        if align == "left":
            cost = x0 - lo
        elif align == "right":
            cost = hi - x1
        else:
            cost = abs((x0 - lo) - (hi - x1))
        if best is None or cost < best[0]:
            best = (cost, x, m)
    if best is None:
        return f"no x keeps the ink inside the box with a {margin} px margin"
    return best[1], y, best[2]


def suggest(src, text: str, box=(0, 0, 64, 64), role: str = "auto", align: str = "center",
            valign: str = "center", max_lines: Optional[int] = None, margin: int = 1,
            keep_case: bool = False, keep_breaks: bool = False, hyphenate: bool = False,
            stable: bool = False, only: Optional[Sequence[str]] = None, min_cap: int = 0):
    """Rank every font that can draw `text` inside `box` (x, y, w, h). Returns (candidates, rejections, role)."""
    role = guess_role(text) if role == "auto" else role
    if role in ("value", "time") and max_lines is None:
        max_lines = 1
    cands: List[Candidate] = []
    rejected: List[Rejection] = []
    if not str(text).strip():
        return cands, [Rejection("(all)", "the text is empty: nothing to draw")], role
    known = F.font_keys(src)
    for key in (only or known):
        key = key.strip().lower().replace("font_", "")
        if key not in known:
            rejected.append(Rejection(key, "unknown font name (the integration would draw pico_8)"))
            continue
        info = F.info(src, key)
        font = F.get(src, key)
        if info.cap_height < min_cap:
            rejected.append(Rejection(key, f"capitals are {info.cap_height} px, below --min-cap {min_cap}"))
            continue
        statuses = []
        bad = []
        for ch in sorted(set(text) - {" ", "\n"}):
            g = F.glyph(src, font, ch)
            statuses.append(g.status)
            if g.problem or (keep_case and g.status == F.CASE) or unicodedata.combining(ch):
                bad.append(ch)
        if keep_case and any(c.islower() for c in text) and info.lowercase not in ("true", "small-caps"):
            rejected.append(Rejection(key, f"lower case is {info.lowercase}: it would look like capitals"))
            continue
        if bad:
            why = f"cannot draw {' '.join(bad)}"
            stem = text.rstrip()
            while stem and stem[-1] in bad:
                stem = stem[:-1]
            if stem and stem != text.rstrip() and not any(c in bad for c in stem) and any(c.isdigit() for c in stem):
                why += f" (it can draw '{stem.strip()}': put the unit in a second, smaller component)"
            elif "-" in bad and info.cap_height >= 11 and any(c.isdigit() for c in text):
                why += " (draw the minus as a filled rectangle: references/layout.md#symbols-a-font-lacks)"
            rejected.append(Rejection(key, why))
            continue
        width = box[2] - 2 * margin
        lines = wrap(src, key, text, width, max_lines, keep_breaks, hyphenate)
        if lines is None:
            longest = max(str(text).replace("\n", " ").split() or [""], key=lambda w: font.get_text_width(w))
            why = (f"'{longest}' alone is {font.get_text_width(longest)} px, the box allows {width} px"
                   if font.get_text_width(longest) > width else f"needs more than {max_lines} line(s)")
            rejected.append(Rejection(key, why))
            continue
        placed = _place(src, key, lines, box, align, valign, stable, info, margin)
        if isinstance(placed, str):
            rejected.append(Rejection(key, placed))
            continue
        x, y, m = placed
        score, reasons = _score(info, role, text, lines, statuses)
        cands.append(Candidate(key, lines, (x, y), align, m.ink, info.cap_height, score, reasons, m))
    cands.sort(key=lambda c: (-c.score, c.font))
    return cands, rejected, role


# ---------------------------------------------------------------- budgets for templated text

def budget(src, font_name, width: int) -> Dict[str, object]:
    """How many characters of each kind fit in `width` px (worst case = widest glyph of the class)."""
    font, _ = F.resolve(src, font_name)
    out: Dict[str, object] = {"font": getattr(font, "name", font_name), "width": width}
    classes = {"digits": string.digits, "upper": string.ascii_uppercase, "lower": string.ascii_lowercase}
    for name, chars in classes.items():
        ok = [c for c in chars if F.glyph(src, font, c).status in (F.OK, F.CASE)]
        if len(ok) < len(chars):  # a class the font cannot fully draw has no useful budget
            out[name] = None
            continue
        widest = max(ok, key=lambda c: font.get_text_width(c))
        typical = "0" if name == "digits" else ("E" if name == "upper" else "e")
        out[name] = {"worst_case": F.capacity(font, widest, width, src), "widest": widest,
                     "typical": F.capacity(font, typical, width, src)}
    return out


def strip_templates(text: str) -> Tuple[str, int, bool]:
    """Remove `{{ ... }}` blocks. Returns (static text, number of blocks, has `{% %}` logic)."""
    logic = "{%" in text
    n = len(re.findall(r"{{.*?}}", text, flags=re.S))
    return re.sub(r"{{.*?}}", "", text, flags=re.S), n, logic


def is_templated(value) -> bool:
    return isinstance(value, str) and ("{{" in value or "{%" in value)
