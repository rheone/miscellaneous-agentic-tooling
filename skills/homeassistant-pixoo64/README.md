# homeassistant-pixoo64 skill

An agent skill for designing pages for a Divoom Pixoo 64 driven by the Home Assistant integration [gickowtf/pixoo-homeassistant](https://github.com/gickowtf/pixoo-homeassistant) (domain `divoom_pixoo`). It is written for release **1.24.0 – BDF Fonts & Pixoo API Fallback** (2026-09-30) and checked against that release's source code on 2026-11-08, and on a Pixoo 64 with a calibration page: every position in the photos matched the tool's preview. Colors were not verified (the photos had a camera color cast).

It replaces the earlier version of this skill (1.0.2), which was written for 1.23 and earlier and has several facts that 1.24.0 changed (see [references/changes.md](references/changes.md)).

## What problem it solves

The Pixoo draws text exactly where you put it. Nothing wraps, nothing warns. A line that is too wide is cut off, a character the font does not have turns into `?` or disappears, a color name with a capital letter becomes white, and a dot over an `i` can land above the top row. Each font has its own height, spacing, character set and quirks, and 1.24.0 added five BDF fonts and custom fonts.

The skill gives an agent (and you) Python tools that run the integration's own font code, so they show what the device will draw before you send it.

## How you use it

Ask Claude, for example "show 'Garage door open' on the Pixoo". The skill loads by itself. Claude runs the tools, shows you a PNG preview, and then sends the page. You only run the commands below when you want to check something yourself.

## Words used here

| Word | Meaning |
|---|---|
| Glyph | The drawing of one character in a font. |
| BDF | A plain-text file format for pixel fonts. 1.24.0 can load them. |
| Matrix font | One of the five older fonts built into the integration's code (`gicko`, `five_pix`, `eleven_pix`, `clock`, `pix24`). |
| Cap line | The top row of a capital letter. The `y` in a text `position` points here. |
| Baseline | The bottom row of a capital letter. Letters like `g` and `y` hang below it. |
| Advance | How far along the next letter starts, including the space after the letter. |
| Ink box | The rectangle the lit pixels really cover. |
| Lint | Check a file for mistakes without running it. |
| CSS4 color name | A web color name such as `lightskyblue`, written in lower case. |
| Template | A `{{ ... }}` expression that Home Assistant fills in when the page is sent. |
| `-I` | Runs Python in isolated mode, so no stray files from the current folder are loaded. |

## Folder layout

| Path | What |
|---|---|
| `SKILL.md` | What the agent reads first: workflow, rules, font starting points, links |
| `references/` | Loaded only when needed: fonts, layout, pages, operations, custom fonts, troubleshooting, changes, a verification checklist, design themes and ideas, lessons from real configurations |
| `examples/` | Tested example pages (each one is linted by the test suite with its worst-case samples), and `sprites/` pixel art for `sprite` |
| `tools/pixoo.py` | The command line tool |
| `tools/pixoo_kit/` | Its code; `vendor/divoom_pixoo/` is a copy of the 1.24.0 font code and fonts |
| `tools/tests/` | Unit tests (standard library `unittest`) |

## Requirements

- Python 3.9 or newer. No packages are needed.
- PyYAML, only to read `.yaml` files (`render`, `lint`). JSON input works without it.

## Quick start

Run from the skill folder. On Windows use `py` instead of `python`.

```
python -I tools/pixoo.py fonts                                  # compare all fonts
python -I tools/pixoo.py coverage "72°F µg/m³ Café →"           # which fonts can draw these
python -I tools/pixoo.py suggest "Garage door open" --box 0,20,64,24
python -I tools/pixoo.py measure "WET LOAD WAITING" --font five_pix --x 32 --y 30
python -I tools/pixoo.py render examples/notification.yaml --fill 21:45 --png preview.png
python -I tools/pixoo.py lint /config/automations.yaml /config/scripts.yaml
```

Every command has `-h` and most have `--json`.

### Commands

| Command | Use it to |
|---|---|
| `fonts` | See every font side by side: line height, capital height, lower case, digit width, characters per line |
| `font NAME [--glyphs [CHARS]]` | See one font's anatomy and notes; `--glyphs` lists each character's status, advance and ink box |
| `specimen TEXT [--font NAME]` | Draw text in one or all fonts as `#` and `.`, with the cap line, x-height and baseline marked |
| `coverage CHARS [--font NAME]` | Check which fonts draw each character: `ok`, drawn as capital, ASCII stand-in, missing, or empty |
| `measure TEXT --font F --x X --y Y --align A [--draw]` | Place one text and get its width, ink box, clipping and glyph problems, with fixes |
| `suggest TEXT [--box x,y,w,h] [--role ...]` | Rank fonts that fit a box, with reasons, the wrap, the position and ready YAML |
| `budget [--font F] --width W [--pattern=SAMPLE]` | See how many digits or letters fit, for templated values |
| `render FILE [--fill SAMPLE] [--png OUT]` | Preview a page as text and PNG, and list problems |
| `lint FILES... [--alias TEXT]` | Find problems in every Pixoo page in automation and script files |
| `jinja --font F [--chars C] [--var V]` | Get Jinja that computes a text's pixel width inside Home Assistant (checked against Home Assistant's template engine) |
| `sprite ART.txt --x X --y Y [--scale N] [--palette "#=gold,o=white"]` | Turn ASCII pixel art into rectangle components: icons with no image file |
| `doctor` | See which integration copy and font folders are used, and font file problems |

Global options: `--integration DIR` (use this integration folder), `--vendored` (use the bundled 1.24.0 copy), `--config DIR` (Home Assistant config folder, for `/config/fonts` and image paths).

Text that starts with `-` must follow `--`: `measure --font pix24 -- "-5°"`. Patterns use `=`: `--pattern=-88.8°F`.

### Reading `suggest`

```
1. tiny5  score 20.0  -> Garage door open
   why: 5 px capitals, 1 line(s); real lower case
   position [32, 29], ink box (3, 29, 60, 34)
...
Not suitable:
  eleven_pix   3 line(s) of 12 px do not fit the 24 px box height
  pix24        cannot draw G a d e g n o p r
```

The score is a ranking aid, not a measure of quality. The reasons and the "Not suitable" list are the useful part. Roles (`--role`): `headline` prefers big, `body` prefers 5-7 px with real lower case, `value` prefers big fonts whose digits are all one width, `label` prefers small, `time` is a value on one line. `auto` guesses from the text.

### Templates

The tools cannot run Jinja. Anything they could not check is reported as a `not-checked` WARNING, so a clean result means the whole page was checked. Give samples with `--fill` (repeatable):

- `--fill 88` replaces every `{{ ... }}` in text that has no own sample;
- `--fill 2=TEXT` replaces the whole content of `components[2]` (also content with `{% %}` logic);
- `--fill 1.position=19,24` replaces a templated position (also `size`, `color`).

Run `render` once per worst case: longest text, widest number, a negative value, one line versus two.

`suggest --min-cap 7` keeps only fonts with capitals at least 7 px tall, for text read from across a room.

## How it works

The tools never re-implement the renderer. They load `pixoo64/_bdf.py` and `pixoo64/_font.py` from the integration and draw on a mock 64 x 64 canvas, so widths, line heights, fallbacks and positions match the device code. They look for the integration in this order:

1. `--integration DIR`, or the environment variable `PIXOO_INTEGRATION_DIR`
2. `custom_components/divoom_pixoo` in the current folder or a parent of it, or of the skill folder, or `/config/custom_components/divoom_pixoo`
3. The bundled copy in `tools/pixoo_kit/vendor/divoom_pixoo` (1.24.0)

The first output line names the copy in use. If the installed integration is not 1.24.0 or its font code differs from the bundled copy, it prints a warning: the measurements still follow the installed code, but the text of this skill may be out of date.

Limits:

- Images are drawn as a placeholder box (no Pillow). The size comes from the PNG, GIF or JPEG header when the file can be read.
- Contrast is a WCAG-style ratio against the color under the text; over images it is not judged.
- Positions were compared with photos of a real Pixoo 64 (`examples/calibration.yaml`); colors were not.

## Tests

```
cd tools
python -I -m unittest discover -s tests -t tests
```

The tests use the bundled 1.24.0 copy, so they give the same result on any machine. Many of them pin facts of 1.24.0 (line heights, missing glyphs, alignment). When a new integration release changes those facts, the tests fail and show what to re-check.

## Updating to a new integration release

1. Copy `pixoo64/_bdf.py`, `pixoo64/_font.py`, `pixoo64/_colors.py`, `fonts/` and `manifest.json` from the new release into `tools/pixoo_kit/vendor/divoom_pixoo/`.
2. Set `BASED_ON` in `tools/pixoo_kit/source.py`.
3. Run the tests. Each failure is a changed fact: update the test, then the matching reference page.
4. Read the release notes for changes outside fonts (pages, services, components) and update `references/`.
5. Update the version fields in the `SKILL.md` front matter.

## Licenses

- This skill: Apache-2.0.
- `tools/pixoo_kit/vendor/divoom_pixoo/`: code from gickowtf/pixoo-homeassistant, MIT (`LICENSE` there). Fonts: Tiny5, Tiny5 Duo, Pixelify Sans and Press Start 2P under the SIL Open Font License 1.1 (`fonts/licenses/`), PICO-8 under CC0. See `fonts/CREDITS.md`.
