"""Render a `page_data` dict like divoom_pixoo 1.24.0 and lint it.

Covers what `sensor.py` does for `components` pages: draw order, font lookup, color
rules, rectangle math, image placement. Images are drawn as a placeholder box
(the tool has no Pillow); their size comes from the file header when the file is
readable, else from `width`/`height`, else 64x64.
"""
from __future__ import annotations

import ast
import os
import re
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from . import fonts as F
from . import text as T

CANVAS = 64
PAGE_TYPES = ("components", "custom", "clock", "channel", "visualizer", "gif", "pv", "fuel", "progress_bar")
REQUIRED = {
    "clock": ("id",), "channel": ("id",), "visualizer": ("id",), "gif": ("gif_url",),
    "pv": ("power", "storage", "discharge", "powerhousetotal", "vomNetz", "time"),
    "fuel": ("title", "name1", "price1", "name2", "price2", "name3", "price3", "status"),
    "progress_bar": ("header", "progress", "footer"),
}
RESAMPLE = ("box", "nearest", "pixel_art", "bilinear", "hamming", "bicubic", "antialias", "lanczos")
IMAGE_KEYS = ("type", "image_path", "image_url", "image_data", "position", "width", "height", "resample_mode")
TEXT_KEYS = ("type", "content", "position", "font", "color", "align")
RECT_KEYS = ("type", "position", "size", "color", "filled")


@dataclass
class Finding:
    rule: str
    severity: str        # error | warning | info
    where: str
    message: str

    def as_dict(self):
        return dict(self.__dict__)


class Fill:
    """Sample values for templated fields.

    Each spec is one of:
      VALUE          replaces every {{ }} block in text content that has no own sample
      N=VALUE        replaces the whole content of components[N]
      N.FIELD=VALUE  replaces another field of components[N] (position/size as "x,y", color as a name or "r,g,b")
    `\\n` in a value is a line break.
    """

    def __init__(self, specs=None):
        self.default: Optional[str] = None
        self.fields: Dict[Tuple[int, str], str] = {}
        if isinstance(specs, str):
            specs = [specs]
        for spec in specs or []:
            m = re.match(r"^(\d+)(?:\.([a-z_]+))?=(.*)$", spec, flags=re.S)
            if m:
                self.fields[(int(m.group(1)), m.group(2) or "content")] = m.group(3).replace("\\n", "\n")
            else:
                self.default = spec.replace("\\n", "\n")

    def __bool__(self):
        return self.default is not None or bool(self.fields)

    def apply(self, i: int, comp: Dict) -> Tuple[Dict, List[str]]:
        """Copy of `comp` with this component's samples applied, and the names of the fields replaced."""
        out, used = dict(comp), []
        for (idx, field_name), value in self.fields.items():
            if idx != i:
                continue
            used.append(field_name)
            try:
                if field_name in ("position", "size"):
                    out[field_name] = [int(v) for v in value.split(",")]
                elif field_name == "color" and "," in value:
                    out[field_name] = [int(v) for v in value.split(",")]
                elif field_name in ("width", "height"):
                    out[field_name] = int(value)
                else:
                    out[field_name] = value
            except ValueError:
                raise SystemExit(f"--fill {i}.{field_name}={value}: expected whole numbers, e.g. {i}.{field_name}=32,20")
        return out, used


def _templated_any(value) -> bool:
    return T.is_templated(value) or (isinstance(value, (list, tuple)) and any(T.is_templated(v) for v in value))


@dataclass
class Rendered:
    pixels: List[List[Tuple[int, int, int]]]
    owner: List[List[int]]                 # index of the component that last drew each pixel, -1 = none
    findings: List[Finding] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)


def _colors(src):
    """CSS4 color table of the integration (lives in _colors.py, which imports Home Assistant)."""
    path = os.path.join(src.integration_dir, "pixoo64", "_colors.py")
    table = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for m in re.finditer(r"'([a-z]+)':\s*'#([0-9A-Fa-f]{6})'", fh.read()):
                h = m.group(2)
                table[m.group(1)] = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except OSError:
        pass
    if not table:
        table = {"white": (255, 255, 255), "black": (0, 0, 0)}
    return table


_IS_NUMERIC = re.compile(r"^[+-]?(?!0\d)\d*(?:\.\d*)?$")


def ha_native(text: str):
    """What Home Assistant's Template(...).async_render() returns for a rendered string (native types).

    Mirrors homeassistant.helpers.template._parse_result: literal_eval, keep strings as the original text,
    and turn numbers back into numbers only when the text looks like a plain decimal (no leading zero).
    The integration renders every value again with Template(str(value)), so this applies even to plain text.
    """
    try:
        result = ast.literal_eval(text)
    except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
        return text
    if isinstance(result, (str, complex)):
        return text
    if isinstance(result, (int, float)) and not isinstance(result, bool) and _IS_NUMERIC.match(text) is None:
        return text
    return result


def color_of(src, value, where: str, findings: List[Finding], default=(255, 255, 255)):
    """Mirror render_color(): renders to a list -> RGB; an exact lower-case CSS4 name -> RGB; anything else -> default."""
    table = _colors(src)
    if value is None:
        return default
    if T.is_templated(value) or (isinstance(value, (list, tuple)) and any(T.is_templated(v) for v in value)):
        findings.append(Finding("color-templated", "info", where, "color is a template; preview uses white"))
        return default
    rendered = ha_native(str(value)) if not isinstance(value, (list, tuple)) else list(value)
    if isinstance(value, (list, tuple)) or isinstance(rendered, list):
        if isinstance(rendered, tuple):
            rendered = None
        if (not isinstance(rendered, list) or len(rendered) < 3
                or not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in rendered[:3])):
            findings.append(Finding("color-invalid", "error", where, f"color {value!r} is not [R, G, B]"))
            return default
        if any(isinstance(v, float) for v in rendered[:3]):
            findings.append(Finding("color-float", "error", where,
                                    f"color {value!r} has a decimal value: the frame cannot be encoded (TypeError) "
                                    "and the whole page is not sent. Use whole numbers"))
            return default
        if any(v < 0 or v > 255 for v in rendered[:3]):
            findings.append(Finding("color-range", "warning", where, f"color {value!r} is clamped to 0-255"))
        return tuple(max(0, min(255, int(v))) for v in rendered[:3])
    s = str(value)
    if isinstance(rendered, tuple):
        findings.append(Finding("color-unknown", "error", where,
                                f"color '{s}' renders to a tuple, not a list: it silently becomes {default}. Write [R, G, B]"))
        return default
    if s in table:
        return table[s]
    hint = ""
    if s.lower() in table:
        hint = f" (names are case-sensitive: write '{s.lower()}')"
    elif s.startswith("#"):
        hint = " (hex is not supported: write [R, G, B])"
    findings.append(Finding("color-unknown", "error", where,
                            f"color '{s}' is not a lower-case CSS4 name or [R, G, B]: it silently becomes the default {default}{hint}"))
    return default


def _luminance(rgb):
    def ch(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b) -> float:
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def image_size(path: str) -> Optional[Tuple[int, int]]:
    """Width and height from a PNG, GIF or JPEG header (stdlib only)."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(26)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                return struct.unpack(">II", head[16:24])
            if head[:6] in (b"GIF87a", b"GIF89a"):
                return struct.unpack("<HH", head[6:10])
            if head[:2] == b"\xff\xd8":
                fh.seek(2)
                while True:
                    marker = fh.read(2)
                    if len(marker) < 2 or marker[0] != 0xFF:
                        return None
                    if marker[1] in (0xC0, 0xC1, 0xC2):
                        fh.read(3)
                        h, w = struct.unpack(">HH", fh.read(4))
                        return w, h
                    (length,) = struct.unpack(">H", fh.read(2))
                    fh.seek(length - 2, 1)
    except (OSError, struct.error):
        return None
    return None


def _thumbnail(size, box):
    """PIL Image.thumbnail: shrink to fit `box`, keep aspect, never enlarge."""
    w, h = size
    bw, bh = box
    if w <= bw and h <= bh:
        return w, h
    scale = min(bw / w, bh / h)
    return max(1, round(w * scale)), max(1, round(h * scale))


def _int_pair(value, where, name, findings):
    if _templated_any(value):
        n = where[len("components["):-1] if where.startswith("components[") else "N"
        findings.append(Finding("not-checked", "warning", where,
                                f"{name} is a template, so this component was NOT drawn or checked; "
                                f"add --fill {n}.{name}=x,y"))
        return None
    try:
        a, b = value
        return int(a), int(b)
    except (TypeError, ValueError):
        findings.append(Finding(f"{name}-invalid", "error", where, f"{name} must be [x, y], got {value!r}"))
        return None


def _local_path(src, path: str, config_dir: Optional[str]) -> Optional[str]:
    if not config_dir:
        return None
    p = path.replace("\\", "/")
    if p.startswith("/config/"):
        return os.path.join(config_dir, *p[len("/config/"):].split("/"))
    return None


def render(src, page: Dict, fill: Optional[str] = None, context: str = "service",
           config_dir: Optional[str] = None) -> Rendered:
    """Render and lint one page. `context` is "service" (show_message) or "config" (pages_data)."""
    px = [[(0, 0, 0)] * CANVAS for _ in range(CANVAS)]
    owner = [[-1] * CANVAS for _ in range(CANVAS)]
    out = Rendered(px, owner)
    fnd = out.findings
    ptype = str(page.get("page_type", "")).lower()
    if not ptype:
        fnd.append(Finding("page-type-missing", "error", "page", "no page_type: show_message logs 'No page to render.'"))
        return out
    if ptype == "visualiser":
        fnd.append(Finding("page-type-unknown", "error", "page",
                           "'visualiser' is not accepted in 1.24.0 (the code only checks 'visualizer'); nothing is drawn"))
        return out
    if ptype not in PAGE_TYPES:
        fnd.append(Finding("page-type-unknown", "error", "page", f"page_type '{ptype}' is unknown: nothing is drawn"))
        return out
    for key in REQUIRED.get(ptype, ()):
        if key not in page:
            fnd.append(Finding("page-field-missing", "error", "page", f"{ptype} page needs '{key}' (KeyError at render)"))
    if ptype == "visualizer" or ptype == "channel" or ptype == "clock" or ptype == "gif":
        fnd.append(Finding("page-device-drawn", "info", "page", f"{ptype} pages are drawn by the device; no preview"))
        return out
    if ptype in ("pv", "fuel", "progress_bar"):
        _lint_special(ptype, page, fnd)
        return out
    if "variables" in page and context == "service":
        fnd.append(Finding("variables-in-service", "warning", "page",
                           "`variables` in a service call: Home Assistant renders the page templates first, "
                           "so references to these variables are empty. Use script variables instead."))
    comps = page.get("components")
    if T.is_templated(comps):
        fnd.append(Finding("not-checked", "warning", "page",
                           "components is one template and was NOT checked: render it in Home Assistant "
                           "(ha_eval_template) and lint the resulting list"))
        return out
    if not isinstance(comps, list):
        fnd.append(Finding("components-missing", "error", "page", "components page needs a `components` list"))
        return out
    fill = fill if isinstance(fill, Fill) else Fill(fill)
    text_boxes = []
    for i, comp in enumerate(comps):
        where = f"components[{i}]"
        if not isinstance(comp, dict):
            fnd.append(Finding("component-invalid", "error", where, "component is not a mapping"))
            out.labels.append(f"{i}:invalid")
            continue
        comp, used = fill.apply(i, comp)
        if used:
            fnd.append(Finding("sample", "info", where, f"sample used for {', '.join(used)}"))
        ctype = comp.get("type")
        out.labels.append(f"{i}:{ctype}")
        if ctype == "text":
            _text(src, comp, i, where, out, fill, context, text_boxes)
        elif ctype == "rectangle":
            _rect(src, comp, i, where, out)
        elif ctype == "image":
            _image(src, comp, i, where, out, config_dir)
        elif ctype == "templatable":
            fnd.append(Finding("not-checked", "warning", where,
                               "templatable output was NOT checked: render the template and lint the components it makes"))
        else:
            fnd.append(Finding("component-type-unknown", "error", where, f"type '{ctype}' is ignored by the integration"))
    _overlaps(text_boxes, fnd)
    unchecked = sorted({f.where for f in fnd if f.rule == "not-checked" and f.where.startswith("components")})
    if unchecked:
        idx = ", ".join(w[len("components["):-1] for w in unchecked)
        fnd.append(Finding("not-checked-summary", "warning", "page",
                           f"{len(unchecked)} of {len(comps)} components were not fully checked ({idx}). "
                           f"Give samples: --fill N=TEXT, --fill N.position=x,y. Render one sample per worst case."))
    return out


def _unknown_keys(comp, allowed, where, fnd, extra_msg=None):
    for k in comp:
        if k not in allowed:
            msg = extra_msg.get(k) if extra_msg and k in extra_msg else f"'{k}' is not read by the integration"
            fnd.append(Finding("key-ignored", "warning", where, msg))


def _text(src, comp, i, where, out: Rendered, fill, context, text_boxes):
    fnd = out.findings
    _unknown_keys(comp, TEXT_KEYS, where, fnd, {"size": "'size' is ignored on text; the font sets the size"})
    if "content" not in comp or "position" not in comp:
        fnd.append(Finding("text-field-missing", "error", where, "text needs `content` and `position` (KeyError)"))
        return
    pos_val = comp["position"]
    if context == "config" and (T.is_templated(pos_val) or (isinstance(pos_val, list) and any(T.is_templated(v) for v in pos_val))):
        fnd.append(Finding("text-position-templated", "error", where,
                           "text position is not template-rendered in pages_data (only rectangle position/size are)"))
        return
    pos = _int_pair(pos_val, where, "position", fnd)
    if pos is None:
        return
    font_name = comp.get("font", "")
    font, fell_back = F.resolve(src, font_name)
    content = str(comp["content"])
    if T.is_templated(content):
        static, n, logic = T.strip_templates(content)
        b = T.budget(src, font_name, CANVAS - 2)
        caps = (b.get("upper") or {}).get("worst_case", "?")
        digs = (b.get("digits") or {}).get("worst_case", "?")
        room = f"one 62 px line of {font.name.lower()} holds {digs} digits or {caps} wide capitals"
        if fill.default is not None and not logic:
            content = re.sub(r"{{.*?}}", fill.default, content, flags=re.S)
            fnd.append(Finding("sample", "info", where, f"template blocks filled with '{fill.default}' for the preview"))
        elif logic:
            fnd.append(Finding("not-checked", "warning", where,
                               f"content has {{% %}} logic and was NOT checked; {room}. Add --fill {i}=SAMPLE"))
            return
        else:
            fnd.append(Finding("not-checked", "warning", where,
                               f"{n} template block(s) not filled: only the fixed text '{static.strip()}' was checked; "
                               f"{room}. Add --fill {i}=SAMPLE (one run per worst case)"))
            content = static
    native = ha_native(content)
    if not isinstance(native, str):
        drawn = str(native)
        if drawn != content:
            fnd.append(Finding("text-native-type", "warning", where,
                               f"'{content}' is parsed as {type(native).__name__} by Home Assistant and drawn as '{drawn}'. "
                               "Keep a unit or other text in the same content"))
        content = drawn
    color = color_of(src, comp.get("color"), where, fnd)
    align = str(comp.get("align", "") or "")
    m = T.measure(src, font_name, content, pos[0], pos[1], align)
    shown = content.replace("\n", "\\n")
    for msg in m.issues:
        sev = "error" if msg.startswith(("not in ", "empty glyph", "unknown font")) or "fall off" in msg else "warning"
        fnd.append(Finding("text", sev, where, f"'{shown}': {msg}"))
    for msg in m.hints:
        fnd.append(Finding("text-hint", "info", where, f"'{shown}': {msg}"))
    if content.strip() and not m.ink:
        fnd.append(Finding("text-invisible", "error", where, f"'{shown}' draws no pixels"))
    bg_samples, over_image = [], False
    for (x, y) in m.pixels:
        if 0 <= x < CANVAS and 0 <= y < CANVAS:
            o = out.owner[y][x]
            if o >= 0 and out.labels[o].endswith(":image"):
                over_image = True
            bg_samples.append(out.pixels[y][x])
            out.pixels[y][x] = color
            out.owner[y][x] = i
    if over_image:
        fnd.append(Finding("text-over-image", "info", where,
                           f"'{shown}' is drawn over an image; check its contrast on the preview or device"))
    elif bg_samples:
        bg = max(set(bg_samples), key=bg_samples.count)
        ratio = contrast(color, bg)
        if ratio < 3.0:
            fnd.append(Finding("contrast", "warning", where,
                               f"'{content}' color {color} on background {bg}: contrast {ratio:.1f}:1 (aim for 3:1 or more)"))
    if m.ink:
        text_boxes.append((i, shown, set(p for p in m.pixels), m.ink))


def _line(a, b):
    """_pixoo.draw_line: lerp over max(|dx|, |dy|) steps, end point excluded, Python round()."""
    steps = max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    pts = set()
    for step in range(steps):
        t = step / steps
        pts.add((round(a[0] + t * (b[0] - a[0])), round(a[1] + t * (b[1] - a[1]))))
    return list(pts)


def _rect(src, comp, i, where, out: Rendered):
    fnd = out.findings
    _unknown_keys(comp, RECT_KEYS, where, fnd)
    if "position" not in comp or "size" not in comp:
        fnd.append(Finding("rect-field-missing", "error", where, "rectangle needs `position` and `size` (KeyError)"))
        return
    pos = _int_pair(comp["position"], where, "position", fnd)
    size = _int_pair(comp["size"], where, "size", fnd)
    if pos is None or size is None:
        return
    color = color_of(src, comp.get("color"), where, fnd)
    filled_raw = comp.get("filled", True)
    if "filled" not in comp:
        fnd.append(Finding("rect-filled-default", "info", where, "no `filled`: rectangles are FILLED by default"))
    # sensor.py: bool(Template(str(filled)).async_render()) -> native types decide
    filled = bool(ha_native(str(filled_raw)))
    if isinstance(filled_raw, str) and filled and filled_raw.strip().lower() in ("false", "no", "off"):
        fnd.append(Finding("rect-filled-string", "warning", where,
                           f"filled: '{filled_raw}' stays a non-empty string, so the rectangle is FILLED. "
                           "Write filled: false (YAML boolean)"))
    x, y = pos
    w, h = size[0] - 1, size[1] - 1
    if size[0] <= 0 or size[1] <= 0 or (not filled and size[0] <= 1 and size[1] <= 1):
        fnd.append(Finding("rect-size", "warning", where, f"size {list(size)} draws a degenerate rectangle"))
    pts = []
    if filled:  # _pixoo.draw_filled_rectangle
        pts = [(xx, yy) for yy in range(y, y + h + 1) for xx in range(x, x + w + 1)]
    else:  # four _pixoo.draw_line calls, each without its end point
        corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
        for a, b in zip(corners, corners[1:]):
            pts += _line(a, b)
    off = 0
    for (xx, yy) in pts:
        if 0 <= xx < CANVAS and 0 <= yy < CANVAS:
            out.pixels[yy][xx] = color
            out.owner[yy][xx] = i
        else:
            off += 1
    if off:
        fnd.append(Finding("rect-off-canvas", "info", where, f"{off} px of the rectangle fall off the display"))


def _image(src, comp, i, where, out: Rendered, config_dir):
    fnd = out.findings
    _unknown_keys(comp, IMAGE_KEYS, where, fnd, {"align": "'align' is ignored on images; position is the top-left corner"})
    sources = [k for k in ("image_path", "image_url", "image_data") if k in comp]
    if not sources:
        fnd.append(Finding("image-source-missing", "error", where, "image needs image_path, image_url or image_data; skipped"))
        return
    if len(sources) > 1:
        fnd.append(Finding("image-source-many", "warning", where, f"several sources {sources}: only {sources[0]} is used"))
    if "position" not in comp:
        fnd.append(Finding("image-position-missing", "error", where, "image needs `position` (KeyError)"))
        return
    pos = _int_pair(comp["position"], where, "position", fnd)
    if pos is None:
        return
    mode = str(comp.get("resample_mode", "box")).lower()
    if mode not in RESAMPLE and not T.is_templated(mode):
        fnd.append(Finding("image-resample", "warning", where, f"resample_mode '{mode}' is unknown: box is used"))
    size = None
    if sources[0] == "image_path" and not T.is_templated(comp["image_path"]):
        local = _local_path(src, str(comp["image_path"]), config_dir)
        if local:
            if os.path.isfile(local):
                size = image_size(local)
            else:
                fnd.append(Finding("image-not-found", "error", where, f"{comp['image_path']} does not exist"))
    w, h = comp.get("width"), comp.get("height")
    if size:
        if w and h:
            if abs(size[0] / size[1] - w / h) > 0.05:
                fnd.append(Finding("image-distort", "warning", where,
                                   f"width and height both set: the {size[0]}x{size[1]} image is stretched to {w}x{h}"))
            size = (int(w), int(h))
        elif w or h:
            target = (int(w) if w else 100, int(h) if h else 100)
            new = _thumbnail(size, target)
            if new == size and (size[0] < target[0] if w else size[1] < target[1]):
                fnd.append(Finding("image-no-upscale", "warning", where,
                                   f"{size[0]}x{size[1]} image: width/height only shrink (PIL thumbnail), never enlarge"))
            size = new
        size = _thumbnail(size, (CANVAS, CANVAS))
    else:
        size = (int(w), int(h)) if (w and h) else (64, 64)
        fnd.append(Finding("image-size-unknown", "info", where, f"image size unknown; preview assumes {size[0]}x{size[1]}"))
    x, y = pos
    for yy in range(y, y + size[1]):
        for xx in range(x, x + size[0]):
            if 0 <= xx < CANVAS and 0 <= yy < CANVAS:
                out.pixels[yy][xx] = (60, 60, 90) if (xx + yy) % 2 else (40, 40, 60)
                out.owner[yy][xx] = i
    if x + size[0] > CANVAS or y + size[1] > CANVAS or x < 0 or y < 0:
        fnd.append(Finding("image-off-canvas", "warning", where, f"{size[0]}x{size[1]} image at {list(pos)} is cut off"))


def _overlaps(text_boxes, fnd):
    for a in range(len(text_boxes)):
        for b in range(a + 1, len(text_boxes)):
            ia, ta, pa, ba = text_boxes[a]
            ib, tb, pb, bb = text_boxes[b]
            shared = pa & pb
            if shared and ta == tb:
                fnd.append(Finding("text-effect", "info", f"components[{ia}]+[{ib}]",
                                   f"'{ta}' is drawn twice, overlapping: read as a shadow or outline effect"))
            elif shared:
                fnd.append(Finding("text-overlap", "warning", f"components[{ia}]+[{ib}]",
                                   f"'{ta}' and '{tb}' share {len(shared)} pixels. Fix it, or tell the user why it is "
                                   "intended (an effect, a knockout, a deliberate layer)"))
            elif ba[0] <= bb[2] and bb[0] <= ba[2] and (abs(ba[3] - bb[1]) == 1 or abs(bb[3] - ba[1]) == 1):
                fnd.append(Finding("text-touch", "warning", f"components[{ia}]+[{ib}]",
                                   f"'{ta}' and '{tb}' touch with no blank row between them"))


def _lint_special(ptype, page, fnd):
    where = "page"
    if ptype == "progress_bar":
        p = page.get("progress")
        if isinstance(p, (int, float)) and not isinstance(p, bool) and (p < 0 or p > 100):
            fnd.append(Finding("progress-range", "warning", where, "progress outside 0-100"))
        if p is not None and not T.is_templated(p):
            v = ha_native(str(p))
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                fnd.append(Finding("progress-int", "error", where,
                                   f"progress '{p}' is not a number: int() raises ValueError and the page is not drawn"))
            elif isinstance(v, float):
                fnd.append(Finding("progress-int", "info", where, f"progress {p} is truncated to {int(v)}"))
        if T.is_templated(p) and "int" not in str(p) and "float" not in str(p):
            fnd.append(Finding("progress-int", "warning", where,
                               "add `| int(0)`: 'unavailable' or 'unknown' raises ValueError and the page is not drawn"))
        fnd.append(Finding("special-fonts", "info", where, "header/footer use five_pix: no ' / & + ( ) characters; "
                           "about 13 characters per line; time_end keeps only digits and ':'"))
    if ptype == "pv":
        fnd.append(Finding("pv-numbers", "info", where, "every value except time must render to a number "
                           "(float()); 'unavailable' stops the page. Use `| float(0)`"))
    if ptype == "fuel":
        fnd.append(Finding("fuel-fonts", "info", where, "title: eleven_pix upper case (about 9 characters); "
                           "names: five_pix; prices: gicko"))


def ascii_art(r: Rendered, rows=(0, CANVAS)) -> str:
    """64-column text picture. Each component index gets its own mark; '.' = black."""
    marks = "0123456789abcdefghijklmnopqrstuvwxyz"
    lines = []
    for y in range(rows[0], rows[1]):
        row = []
        for x in range(CANVAS):
            o = r.owner[y][x]
            row.append("." if o < 0 or r.pixels[y][x] == (0, 0, 0) else marks[o % len(marks)])
        lines.append(f"{y:2d} " + "".join(row))
    ruler = "   " + "".join(str(x // 10) if x % 10 == 0 else " " for x in range(CANVAS))
    return ruler + "\n" + "\n".join(lines)


def find_pages(node, path="") -> List[Tuple[str, Dict]]:
    """Every dict with a `page_type` in a loaded YAML/JSON tree, with a readable location."""
    found = []
    if isinstance(node, dict):
        if "page_type" in node:
            found.append((path or "page", node))
        label = node.get("alias") or node.get("id")
        for k, v in node.items():
            sub = f"{path}/{k}" if path else str(k)
            if label and k in ("actions", "action", "sequence", "triggers", "conditions"):
                sub = f"{label}"
            found.extend(find_pages(v, sub))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            label = v.get("alias") if isinstance(v, dict) and v.get("alias") else f"{path}[{i}]"
            found.extend(find_pages(v, label if isinstance(v, dict) and v.get("alias") else f"{path}[{i}]"))
    return found
