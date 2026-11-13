"""Command line for the Pixoo font and layout tools. Run `pixoo.py -h` or `pixoo.py <command> -h`."""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List

from . import fonts as F
from . import page as P
from . import png
from . import source
from . import text as T


def _out(args, data, human):
    if getattr(args, "json", False):
        print(json.dumps(data, indent=2, ensure_ascii=False, default=list))
    else:
        print(human() if callable(human) else human)


def _header(src):
    drift = src.drift()
    line = f"# {src.describe()}"
    if drift:
        line += "\n# WARNING: " + "; ".join(drift) + ". Measurements follow this copy; the skill text may be stale."
    return line


def _known(src, name):
    """Exit with a clear message when a font name would silently fall back to pico_8."""
    key = str(name).strip().lower().replace("font_", "")
    if F.get(src, key) is None:
        sys.exit(f"Unknown font '{name}' (the integration would draw pico_8). Known: {', '.join(F.font_keys(src))}")
    return key


def _unescape(s: str) -> str:
    return s.replace("\\n", "\n")


def _grid(points, y_rows, x_cols, marks=None):
    pts = set(points)
    lines = []
    for y in y_rows:
        tag = (marks or {}).get(y, "")
        lines.append(f"{y:3d} {tag:>4} " + "".join("#" if (x, y) in pts else "." for x in x_cols))
    return "\n".join(lines)


# ---------------------------------------------------------------- commands

def cmd_fonts(args, src):
    infos = F.all_info(src)
    if args.json:
        return _out(args, {"source": src.describe(), "drift": src.drift(), "fonts": [i.as_dict() for i in infos]}, "")
    rows = [_header(src), "",
            "font          kind    line  cap  x-ht desc  top  lower-case            tab.digits  per line (0/A/a)  origin",
            "------------  ------  ----  ---  ---- ----  ---  --------------------  ----------  ----------------  --------"]
    for i in infos:
        pl = i.per_line
        rows.append(f"{i.key:<12}  {i.kind:<6}  {i.line_height:>4}  {i.cap_height:>3}  {str(i.x_height or '-'):>4} "
                    f"{i.descender:>4}  {i.ink_top_ascii:>3}  {i.lowercase:<20}  {'yes' if i.tabular_digits else 'no':<10}  "
                    f"{pl['0']:>3}/{pl['A']:>3}/{pl['a']:>3}       {i.origin}")
    rows += ["", "line = y step per line; cap = capital height; x-ht = lower-case height; desc = rows below the baseline;",
             "top = highest ASCII ink row relative to y (negative = drawn above y). `font <name>` for details."]
    print("\n".join(rows))


def cmd_font(args, src):
    try:
        i = F.info(src, args.name.lower().replace("font_", ""))
    except KeyError:
        sys.exit(f"Unknown font '{args.name}'. Known: {', '.join(F.font_keys(src))}")
    font = F.get(src, i.key)
    data = i.as_dict()
    if args.glyphs is not None:
        chars = _unescape(args.glyphs) if args.glyphs else "".join(chr(o) for o in range(32, 127))
        data["glyphs"] = [{"char": g.char, "name": F.char_name(g.char), "status": g.status, "advance": g.advance,
                           "ink": g.ink} for g in (F.glyph(src, font, c) for c in chars)]
    if args.json:
        return _out(args, data, "")
    out = [_header(src), "", f"{i.key}  ({i.name}, {i.kind}, {i.origin})"]
    if i.path:
        out.append(f"  file: {i.path}")
    out += [f"  line height {i.line_height}   capitals rows {i.cap_top}..{i.baseline} ({i.cap_height} px)   "
             f"x-height {i.x_height or '-'}   descender {i.descender}",
             f"  ASCII ink rows {i.ink_top_ascii}..{i.ink_bottom_ascii}   any glyph {i.ink_top_any}..{i.ink_bottom_any}",
             f"  lower case: {i.lowercase}   monospace: {i.monospace}   tabular digits: {i.tabular_digits} "
             f"(digit advance {i.digit_advance[0]}-{i.digit_advance[1]})   space {i.space_advance} px",
             f"  spacing: {i.tracking}",
             f"  glyphs: {i.glyph_count} ({i.blank_count} blank)   ASCII it cannot draw: {i.ascii_missing or 'none'}",
             f"  per 64 px line: " + ", ".join(f"{k!r} x{v}" for k, v in i.per_line.items()),
             f"  coverage: " + ", ".join(f"{k} {v}" for k, v in i.coverage.items())]
    out += ["  notes:"] + [f"   - {n}" for n in i.notes]
    if args.glyphs is not None:
        out.append("")
        out.append("  char  status               adv  ink(x0,y0,x1,y1)  name")
        for g in data["glyphs"]:
            out.append(f"  {g['char']!r:<5} {g['status']:<20} {g['advance']:>3}  {str(g['ink']):<16}  {g['name']}")
    print("\n".join(out))


def cmd_specimen(args, src):
    names = F.font_keys(src) if args.font in (None, "all") else [_known(src, args.font)]
    txt = _unescape(args.text)
    blocks = [_header(src)]
    for name in names:
        font, fb = F.resolve(src, name)
        info = F.info(src, name) if not fb else F.info(src, "pico_8")
        m = T.measure(src, name, txt, 0, 0, "left")
        if not m.pixels:
            blocks.append(f"\n{name}: draws nothing for this text")
            continue
        x1 = max(p[0] for p in m.pixels)
        y0 = min(min(p[1] for p in m.pixels), 0)
        y1 = max(max(p[1] for p in m.pixels), info.baseline)
        marks = {0: "y", info.baseline: "base"}
        if info.x_height:
            marks.setdefault(info.baseline - info.x_height + 1, "x-ht")
        blocks.append(f"\n{name}  width {[l.width for l in m.lines]}  line height {m.line_height}")
        blocks.append(_grid(m.pixels, range(y0, y1 + 1), range(0, x1 + 1), marks))
        for msg in m.issues:
            blocks.append(f"  ! {msg}")
        for msg in m.hints:
            blocks.append(f"  - {msg}")
    print("\n".join(blocks))


def cmd_coverage(args, src):
    chars = _unescape(args.chars)
    names = F.font_keys(src) if not args.font else [_known(src, args.font)]
    table = {}
    for name in names:
        font, _ = F.resolve(src, name)
        table[name] = {c: F.glyph(src, font, c).status for c in dict.fromkeys(chars) if c not in " \n"}
    if args.json:
        return _out(args, table, "")
    uniq = [c for c in dict.fromkeys(chars) if c not in " \n"]
    sym = {F.OK: "ok", F.CASE: "Aa", F.TYPO: "~", F.MISSING: "--", F.BLANK: "__"}
    rows = [_header(src), "", "font          " + " ".join(f"{c:>3}" for c in uniq) + "   verdict"]
    for name, st in table.items():
        bad = [c for c, s in st.items() if s in (F.MISSING, F.BLANK)]
        rows.append(f"{name:<12}  " + " ".join(f"{sym[st[c]]:>3}" for c in uniq) +
                    ("   all drawn" if not bad else f"   cannot draw {''.join(bad)}"))
    rows += ["", "ok = own glyph; Aa = drawn as the capital; ~ = ASCII stand-in; -- = missing ('?' in BDF, nothing in matrix);",
             "__ = code point exists but the glyph is empty (draws a gap)."]
    rows += [f"  {c!r}: {F.char_name(c)}" for c in uniq if not c.isascii()]
    print("\n".join(rows))


def cmd_measure(args, src):
    m = T.measure(src, args.font, _unescape(args.text), args.x, args.y, args.align)
    if args.json:
        return _out(args, m.as_dict(), "")
    out = [_header(src), "",
           f"font {m.font}{' (fell back from ' + m.font_requested + ')' if m.fell_back else ''}  "
           f"align {m.align}  position [{m.x}, {m.y}]  line height {m.line_height}"]
    for l in m.lines:
        out.append(f"  line {l.text!r}: width {l.width} px, pen starts x={l.start_x}, ink {l.ink}")
    out.append(f"  ink box {m.ink}   off-display pixels {m.off_canvas}   verdict: {'OK' if m.fits else 'PROBLEM'}")
    out += [f"  ! {s}" for s in m.issues] + [f"  - {s}" for s in m.hints]
    if args.draw and m.pixels:
        out.append("")
        on = [p for p in m.pixels if 0 <= p[0] < 64 and 0 <= p[1] < 64]
        ys = [p[1] for p in on] or [m.y]
        out.append(_grid(on, range(max(0, min(ys) - 1), min(64, max(ys) + 2)), range(64), {m.y: "y"}))
    print("\n".join(out))


def _box(s: str):
    parts = [int(v) for v in s.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("box is x,y,width,height")
    return tuple(parts)


def cmd_suggest(args, src):
    cands, rejected, role = T.suggest(
        src, _unescape(args.text), args.box, args.role, args.align, args.valign, args.max_lines, args.margin,
        args.keep_case, args.keep_breaks, args.hyphenate, args.stable, args.fonts.split(",") if args.fonts else None,
        args.min_cap)
    if args.json:
        return _out(args, {"role": role, "box": args.box,
                           "candidates": [{"font": c.font, "score": round(c.score, 2), "lines": c.lines,
                                           "position": c.position, "ink": c.ink, "reasons": c.reasons,
                                           "component": c.component(args.color)} for c in cands],
                           "rejected": [r.__dict__ for r in rejected]}, "")
    out = [_header(src), "", f"role: {role}   box x={args.box[0]} y={args.box[1]} w={args.box[2]} h={args.box[3]}   "
           f"align {args.align}/{args.valign}", ""]
    if not cands:
        out.append("No font fits. Shorten the text, widen the box, allow --hyphenate, or split it into two components.")
    for n, c in enumerate(cands[: args.top], 1):
        out.append(f"{n}. {c.font}  score {c.score:.1f}  -> {' | '.join(c.lines)}")
        out.append(f"   why: {'; '.join(c.reasons)}")
        out.append(f"   position [{c.position[0]}, {c.position[1]}], ink box {c.ink}")
    if cands:
        best = cands[0].component(args.color)
        out += ["", "YAML for the best fit:", "  - type: text",
                f"    content: {json.dumps(best['content'], ensure_ascii=False)}",
                f"    font: {best['font']}", f"    color: {best['color']}", f"    align: {best['align']}",
                f"    position: [{best['position'][0]}, {best['position'][1]}]"]
    if rejected:
        out += ["", "Not suitable:"] + [f"  {r.font:<12} {r.reason}" for r in rejected]
    print("\n".join(out))


def cmd_budget(args, src):
    names = F.font_keys(src) if not args.font else [_known(src, args.font)]
    data = [T.budget(src, n, args.width) for n in names]
    if args.pattern:
        for d, n in zip(data, names):
            font, _ = F.resolve(src, n)
            pat = _unescape(args.pattern)
            d["pattern"] = {"text": pat, "width": font.get_text_width(pat),
                            "fits": font.get_text_width(pat) <= args.width,
                            "problems": [g.char for g in T.glyph_report(src, font, pat) if g.problem]}
    if args.json:
        return _out(args, data, "")
    out = [_header(src), "", f"characters that fit in {args.width} px (worst case = widest glyph / typical):", "",
           "font          digits     upper      lower" + ("      pattern" if args.pattern else "")]
    fmt = lambda v: "-" if not v else f"{v['worst_case']:>2} / {v['typical']:<3}"
    for d, n in zip(data, names):
        row = f"{n:<12}  {fmt(d['digits']):<9}  {fmt(d['upper']):<9}  {fmt(d['lower']):<9}"
        if args.pattern:
            p = d["pattern"]
            if p["problems"]:
                row += f"  cannot draw {''.join(p['problems'])}"
            else:
                row += f"  {p['width']:>3} px {'fits' if p['fits'] else 'TOO WIDE'}"
        out.append(row)
    print("\n".join(out))


def _load_any(path: str):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    if path.lower().endswith(".json"):
        try:
            return json.loads(raw)
        except ValueError as exc:
            sys.exit(f"{path}: not valid JSON: {exc}")
    try:
        import yaml  # type: ignore
    except ImportError:
        sys.exit("PyYAML is not installed: pass JSON, or install PyYAML.")

    class Loader(yaml.SafeLoader):
        pass

    def any_tag(loader, suffix, node):
        if isinstance(node, yaml.ScalarNode):
            return f"!{suffix} {loader.construct_scalar(node)}"
        if isinstance(node, yaml.SequenceNode):
            return loader.construct_sequence(node)
        return loader.construct_mapping(node)

    Loader.add_multi_constructor("!", any_tag)
    try:
        return yaml.load(raw, Loader=Loader)
    except yaml.YAMLError as exc:
        sys.exit(f"{path}: not valid YAML: {exc}")


def _print_findings(findings: List[P.Finding], min_sev: str):
    order = {"error": 0, "warning": 1, "info": 2}
    shown = [f for f in findings if order[f.severity] <= order[min_sev]]
    for f in sorted(shown, key=lambda f: order[f.severity]):
        print(f"  {f.severity.upper():<7} {f.where:<22} [{f.rule}] {f.message}")
    return sum(1 for f in findings if f.severity == "error")


def cmd_render(args, src):
    data = _load_any(args.file)
    pages = P.find_pages(data)
    if not pages:
        sys.exit("No page_type found in the file.")
    cfg = args.config or src.config_dir
    errors = 0
    results = []
    for n, (where, pg) in enumerate(pages):
        r = P.render(src, pg, args.fill, args.context, cfg)
        results.append({"where": where, "findings": [f.as_dict() for f in r.findings]})
        if args.json:
            continue
        print(_header(src) if n == 0 else "")
        print(f"== {where}  ({pg.get('page_type')})")
        print(P.ascii_art(r))
        errors += _print_findings(r.findings, args.level)
        if args.png:
            stem, ext = os.path.splitext(args.png)
            target = args.png if len(pages) == 1 else f"{stem}-{n}{ext or '.png'}"
            png.write(target, r.pixels, args.scale, not args.flat)
            print(f"  preview: {os.path.abspath(target)}")
    if args.json:
        _out(args, results, "")
    sys.exit(1 if errors and args.strict else 0)


def cmd_lint(args, src):
    total = 0
    report = []
    for path in args.files:
        data = _load_any(path)
        for where, pg in P.find_pages(data):
            if args.alias and args.alias.lower() not in where.lower():
                continue
            r = P.render(src, pg, args.fill, args.context, args.config or src.config_dir)
            report.append({"file": path, "where": where, "findings": [f.as_dict() for f in r.findings]})
            if args.json:
                continue
            bad = [f for f in r.findings if {"error": 0, "warning": 1, "info": 2}[f.severity] <= {"error": 0, "warning": 1, "info": 2}[args.level]]
            if bad:
                print(f"{path} :: {where}")
                total += _print_findings(r.findings, args.level)
    if args.json:
        _out(args, report, "")
    elif not args.json:
        partial = sum(1 for r in report if any(f["rule"] == "not-checked-summary" or
                                               (f["rule"] == "not-checked" and f["where"] == "page") for f in r["findings"]))
        print(f"\n{total} error(s) in {len(report)} page(s); {partial} page(s) only partly checked "
              f"(templates without samples: see the WARNING lines).")
    sys.exit(1 if total and args.strict else 0)


def cmd_jinja(args, src):
    """Print Jinja that measures text width in Home Assistant exactly like the integration does."""
    font = F.get(src, _known(src, args.font))
    chars = _unescape(args.chars) if args.chars else "".join(chr(o) for o in range(32, 127)) + "°"
    if not args.chars:
        print("{# --chars not given: table covers ASCII and °; pass --chars with every character you use #}")
    bdf = F.is_bdf(font)
    adv = {}
    for c in dict.fromkeys(chars):
        g = F.glyph(src, font, c)
        if g.status in (F.MISSING, F.BLANK) and c != " ":
            continue
        adv[c] = font.get_text_width(c) + (0 if bdf else 1)  # matrix: glyph width + 1 px gap
    common = max(set(adv.values()), key=list(adv.values()).count)
    table = {c: w for c, w in adv.items() if w != common}
    pairs = ", ".join(f"{json.dumps(c, ensure_ascii=False)}: {w}" for c, w in sorted(table.items()))
    var = args.var
    width_expr = "ns.w" if bdf else "ns.w - 1"
    print(f"{{# width in px of `{var}` in {font.name.lower()} (divoom_pixoo {src.version}); "
          f"characters not listed are {common} px; generated by pixoo.py jinja #}}")
    print(f"{{% set adv = {{{pairs}}} %}}")
    print(f"{{% set ns = namespace(w=0) %}}")
    print(f"{{% for c in {var} | string %}}{{% set ns.w = ns.w + adv.get(c, {common}) %}}{{% endfor %}}")
    print(f"{{% set width = [{width_expr}, 0] | max %}}")
    print(f"{{# pen start: left = x; center = x - (width / 2) | int; right = x - width #}}")
    missing = [c for c in dict.fromkeys(chars) if c not in adv]
    if missing:
        print(f"{{# cannot draw: {''.join(missing)} (not in the table) #}}", file=sys.stderr)


def sprite_rects(art: str, x0: int, y0: int, palette: dict, scale: int = 1):
    """ASCII art -> filled rectangles. Each non-space, non-'.' character is a pixel; runs in a row become one
    rectangle, and identical runs in following rows are merged into one taller rectangle."""
    rows = [r.rstrip("\n") for r in art.splitlines()]
    runs = []  # (y, x_start, x_end, char)
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            ch = row[x]
            if ch in " .":
                x += 1
                continue
            start = x
            while x < len(row) and row[x] == ch:
                x += 1
            runs.append((y, start, x - 1, ch))
    open_rects = {}  # (x_start, x_end, char) -> [y_start, y_end]
    done = []
    for y in range(len(rows) + 1):
        current = {(a, b, c) for (yy, a, b, c) in runs if yy == y}
        for key in list(open_rects):
            if key in current and open_rects[key][1] == y - 1:
                open_rects[key][1] = y
                current.discard(key)
            else:
                done.append((key, open_rects.pop(key)))
        for key in current:
            open_rects[key] = [y, y]
    comps = []
    for (a, b, ch), (ys, ye) in sorted(done, key=lambda d: (d[1][0], d[0][0])):
        color = palette.get(ch, palette.get("*", "white"))
        comps.append({"type": "rectangle", "position": [x0 + a * scale, y0 + ys * scale],
                      "size": [(b - a + 1) * scale, (ye - ys + 1) * scale], "color": color, "filled": True})
    return comps


def cmd_sprite(args, src):
    with open(args.file, encoding="utf-8") as fh:
        art = fh.read()
    palette = {}
    for item in (args.palette or "*=white").split(","):
        k, _, v = item.partition("=")
        v = v.strip()
        palette[k.strip() or "*"] = [int(n) for n in v.split(" ")] if " " in v else v
    comps = sprite_rects(art, args.x, args.y, palette, args.scale)
    if args.json:
        return _out(args, comps, "")
    print(f"# {len(comps)} rectangles from {args.file} at [{args.x}, {args.y}], scale {args.scale}")
    for c in comps:
        color = c["color"] if isinstance(c["color"], str) else json.dumps(c["color"])
        print(f"- {{type: rectangle, position: {c['position']}, size: {c['size']}, color: {color}, filled: true}}")


def cmd_doctor(args, src):
    installed = source.find_installed()
    lines = [f"tools based on divoom_pixoo {source.BASED_ON}", f"using: {src.describe()}",
             f"installed copy found: {installed or 'no'}", f"font directories scanned: "]
    for d in src.font_dirs:
        lines.append(f"  {d} {'(exists)' if os.path.isdir(d) else '(missing)'}")
        if os.path.isdir(d):
            for name in sorted(os.listdir(d)):
                if not name.lower().endswith(".bdf"):
                    continue
                stem = os.path.splitext(name)[0].lower()
                ok = "font_" not in stem and F.get(src, stem) is not None
                why = "" if ok else ("  <- contains 'font_': can never be found" if "font_" in stem
                                     else "  <- did not load (see the integration log)")
                lines.append(f"    {name} -> font: {stem}{why}")
    drift = src.drift()
    lines.append("drift: " + ("none" if not drift else "; ".join(drift)))
    lines.append(f"fonts: {', '.join(F.font_keys(src))}")
    print("\n".join(lines))


def build_parser():
    p = argparse.ArgumentParser(prog="pixoo.py", description="Pixoo 64 font and layout tools for divoom_pixoo 1.24.0. "
                                "Every number comes from the integration's own font code.")
    p.add_argument("--integration", help="divoom_pixoo directory to load instead of auto-detect")
    p.add_argument("--vendored", action="store_true", help="use the bundled 1.24.0 snapshot")
    p.add_argument("--config", help="Home Assistant config directory (for /config/fonts and image paths)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, fn, help_):
        s = sub.add_parser(name, help=help_, description=help_)
        s.set_defaults(fn=fn)
        s.add_argument("--json", action="store_true", help="machine-readable output")
        return s

    add("fonts", cmd_fonts, "Compare every font: line height, capital height, lower case, digits, capacity.")
    s = add("font", cmd_font, "Anatomy of one font; --glyphs [CHARS] adds a per-glyph table.")
    s.add_argument("name")
    s.add_argument("--glyphs", nargs="?", const="", default=None)
    s = add("specimen", cmd_specimen, "Draw text in one font or all fonts, with y, x-height and baseline rows marked.")
    s.add_argument("text")
    s.add_argument("--font", default="all")
    s = add("coverage", cmd_coverage, "Which fonts can draw these characters (catches '?', gaps and lost symbols).")
    s.add_argument("chars")
    s.add_argument("--font")
    s = add("measure", cmd_measure, "Place one text component and report width, ink box, clipping and glyph problems.")
    s.add_argument("text")
    s.add_argument("--font", default="pico_8")
    s.add_argument("--x", type=int, default=32)
    s.add_argument("--y", type=int, default=0)
    s.add_argument("--align", default="center")
    s.add_argument("--draw", action="store_true", help="print the rows the text covers")
    s = add("suggest", cmd_suggest, "Rank fonts for text in a box and give the position and YAML.")
    s.add_argument("text")
    s.add_argument("--box", type=_box, default=(0, 0, 64, 64), help="x,y,width,height (default whole display)")
    s.add_argument("--role", choices=T.ROLES, default="auto")
    s.add_argument("--align", choices=T.ALIGNS, default="center")
    s.add_argument("--valign", choices=("top", "center", "bottom"), default="center")
    s.add_argument("--max-lines", type=int)
    s.add_argument("--margin", type=int, default=1, help="blank columns kept at each side of the box")
    s.add_argument("--keep-case", action="store_true", help="reject fonts that draw lower case as capitals")
    s.add_argument("--keep-breaks", action="store_true", help="keep the \\n breaks in the text")
    s.add_argument("--hyphenate", action="store_true", help="split words that do not fit, with '-'")
    s.add_argument("--stable", action="store_true", help="place by font extents, not this text (for templated text)")
    s.add_argument("--fonts", help="comma-separated fonts to consider")
    s.add_argument("--min-cap", type=int, default=0, help="smallest capital height in px (7 = readable across a room)")
    s.add_argument("--color", default="white")
    s.add_argument("--top", type=int, default=5)
    s = add("budget", cmd_budget, "How many characters fit a width: for templated values.")
    s.add_argument("--font")
    s.add_argument("--width", type=int, default=62)
    s.add_argument("--pattern", help="worst-case sample, e.g. '-88.8°F'")
    for name, fn, help_ in (("render", cmd_render, "Preview and lint the page(s) in a YAML/JSON file (ASCII, optional PNG)."),
                            ("lint", cmd_lint, "Lint every Pixoo page in automation/script YAML files.")):
        s = add(name, fn, help_)
        if name == "render":
            s.add_argument("file")
            s.add_argument("--png", help="write a preview PNG here")
            s.add_argument("--scale", type=int, default=8)
            s.add_argument("--flat", action="store_true", help="PNG without LED dot gaps")
        else:
            s.add_argument("files", nargs="+")
            s.add_argument("--alias", help="only pages whose location contains this text")
        s.add_argument("--fill", action="append", metavar="SPEC",
                       help="sample for templates, repeatable: VALUE (every {{ }} in text), N=TEXT (content of "
                            "components[N]), N.position=x,y, N.color=name|r,g,b. Use --fill=VALUE when VALUE starts with '-'")
        s.add_argument("--context", choices=("service", "config"), default="service",
                       help="show_message call (default) or a pages_data entry in the integration options")
        s.add_argument("--level", choices=("error", "warning", "info"), default="warning")
        s.add_argument("--strict", action="store_true", help="exit 1 when there are errors")
    s = add("jinja", cmd_jinja, "Print Jinja that computes a text's pixel width in Home Assistant, for run-time placement.")
    s.add_argument("--font", required=True)
    s.add_argument("--chars", help="only these characters (shorter snippet), e.g. '0123456789.°'")
    s.add_argument("--var", default="text", help="name of the Jinja variable holding the text")
    s = add("sprite", cmd_sprite, "Turn ASCII pixel art (a text file) into rectangle components: icons without image files.")
    s.add_argument("file", help="text file: one character per pixel, '.' or space = off")
    s.add_argument("--x", type=int, default=0)
    s.add_argument("--y", type=int, default=0)
    s.add_argument("--scale", type=int, default=1, help="draw each art pixel as an N x N block")
    s.add_argument("--palette", help="char=color pairs, e.g. '#=gold,o=white,r=255 0 0' (default: all white)")
    add("doctor", cmd_doctor, "Which integration copy and font folders the tools use, and drift from 1.24.0.")
    return p


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    args = build_parser().parse_args(argv)
    src = source.load(args.integration, args.vendored, args.config)
    args.fn(args, src)
