---
name: homeassistant-pixoo64
description: >-
  Pixoo 64 pages through the divoom_pixoo Home Assistant integration (1.24.0).
  Use when the user mentions Pixoo, Divoom or divoom_pixoo and wants to put
  text, a value, an image or a built-in page (clock, gif, progress bar) on it;
  choose a Pixoo font or check a glyph; add a BDF font; or fix a Pixoo page
  that looks wrong.
license: Apache-2.0
metadata:
  author: Robert Engelhardt <rheone@gmail.com>
  version: "2.0.0"
  version-note: "2.0.0 because it replaces this skill's 1.0.2 (written for 1.23 and earlier)"
  source: https://github.com/rheone/miscellaneous-agentic-tooling
  integration: divoom_pixoo (gickowtf/pixoo-homeassistant, MIT)
  integration-release: "1.24.0 – BDF Fonts & Pixoo API Fallback (2026-09-30)"
  integration-source: https://github.com/gickowtf/pixoo-homeassistant/tree/1.24.0
  verified: "2026-11-08: against the 1.24.0 source code, and on a Pixoo 64 with examples/calibration.yaml (all positions matched the render; colors not verified)."
---

# Divoom Pixoo 64 with divoom_pixoo 1.24.0

The integration draws text exactly where you put it: no wrapping, no clipping warning, no uppercasing. Text that is too wide, a glyph the font lacks, or a color name it does not know fails **silently** on the device. The tools below find these failures before the user sees them.

## Tools

```
py -I <this skill>/tools/pixoo.py <command> ...      # Windows; python3 -I elsewhere. Python 3.9+, standard library
```

They import the integration's own font code: the installed `custom_components/divoom_pixoo` when they find it, else the bundled 1.24.0 copy. The first output line says which. A `WARNING` there means the installed version differs from 1.24.0: trust the measured numbers, and treat facts in this skill as possibly stale. PyYAML is needed only to read `.yaml` files. A value that starts with `-` goes after `--` or `=` (`measure --font pix24 -- "-5°"`, `--fill=-5°`).

| Command | Answers |
|---|---|
| `suggest TEXT --box x,y,w,h [--role ...]` | Which fonts fit, ranked with reasons, the wrap, the position, the YAML |
| `coverage CHARS` | Which fonts can draw these characters (`?`, gaps, dropped symbols) |
| `measure TEXT --font F --x --y --align` | Width, ink box, clipping and glyph problems for one component (defaults x 32, align center; the integration's default align is left) |
| `budget --width W [--pattern=SAMPLE]` | How many characters of a templated value fit |
| `render FILE --fill ... --png OUT` | ASCII and PNG preview of a page, plus lint |
| `lint FILE...` | Every Pixoo page in automation or script YAML |
| `jinja --font F --chars CHARS` | Jinja that computes a text's width in Home Assistant, for placement at run time |
| `sprite ART.txt --x --y [--scale] [--palette]` | Rectangle components from ASCII pixel art: icons without image files |

`-h` on any command lists its options and the anatomy commands (`fonts`, `font`, `specimen`, `doctor`).

## Pick the path

- Text, a value or an image on a `components` page: the workflow below.
- Built-in page (`clock`, `channel`, `visualizer`, `gif`, `pv`, `fuel`, `progress_bar`): read [pages](references/pages.md#page-types), then step 7.
- Review or fix existing YAML: `lint FILE`, then `render` each flagged page with samples (step 6). Done when every ERROR is fixed and every WARNING is fixed or explained to the user.
- A page looks wrong on the device: [troubleshooting](references/troubleshooting.md).
- Add a BDF font: [custom fonts](references/custom-fonts.md), and follow its checks.

## Workflow for a components page

1. **Entities.** Find the Pixoo `sensor` (`..._current_page`, the target of every `divoom_pixoo.*` action) and `light` (`..._light`, screen and brightness), for example with `ha_search "pixoo"`. Done when you have both ids from Home Assistant.
2. **Boxes.** Give each piece of content a box `x,y,w,h` (x 0-63 left to right, y 0-63 top to bottom). Components paint in list order, so backgrounds come first. Start from the closest [example](#examples). Done when every component has a box and boxes overlap only where one is a background.
3. **Fonts and positions.** Run `suggest` once per text box. For text read across a room, add `--min-cap 7`. Done when every text component's font and `position` come from `suggest` output.
4. **Glyphs.** Run `coverage` on every character outside `A-Z a-z 0-9` and space (°, %, €, µ, ₂, accents, arrows, quotes, emoji). Done when the verdict for your font is `all drawn`.
5. **Templates.** For each templated value, find its worst cases: longest text, widest number, negative, `unavailable`, one line versus two. Size the slot with `budget`. Text that may wrap needs a fixed number of lines: see [layout](references/layout.md#templated-text). A position that depends on the value can use `jinja`.
6. **Preview.** Write the page to a file. Run `render FILE --png OUT.png` once per worst case, giving each template its sample: `--fill N=TEXT` replaces the content of `components[N]`, `--fill N.position=x,y` a templated position. Read each PNG. Done when every run shows no ERROR and no WARNING (a `not-checked` WARNING means a template still has no sample), or you have told the user why a remaining warning is intended.
7. **Send.** Use `divoom_pixoo.show_message`, through the configuration's display script if it has one. Ask the user how long the page should show if they did not say. Read [operations](references/operations.md) before you choose `duration`, wake the screen, show a time, or write a reusable script.
8. **Verify.** Work through the [checklist](references/checklist.md). Done when every item is checked or reported to the user as unchecked; tell the user the device itself is the final check.

## Rules the tools check

`lint` and `render` report these failures. Apply them whenever you read or write Pixoo YAML.

- **Width**: 5 to 32 characters fit on a 64 px line, depending on font and letters. Take every width from `measure` or `suggest`.
- **Cap line**: `position` y is the top row of a capital letter. Tiny5 and Tiny5Duo draw i-dots above y, PixelifySans some punctuation, and all three draw accents above y (accented capitals up to 7 rows) and descenders below the baseline. Matrix fonts draw only from y down.
- **Case**: 1.24.0 draws text in the case you send. `gicko`, `eleven_pix` and `five_pix` show lower case as capitals; `pico_8` shows it as small capitals. Add `| upper` for the old all-caps look.
- **Missing glyph**: BDF fonts draw `?`; matrix fonts draw nothing and shift centered text by 1 px. `pico_8` draws a gap for accented letters. `pix24` and `eleven_pix` have no `-`, `+` or `!`; `eleven_pix` has no `%`.
- **Colors**: `[R, G, B]` with whole numbers (a decimal stops the whole page), a string that renders to that list, or a lower-case CSS4 name. Other strings (`Red`, `#ff0000`) become white.
- **Rectangles** are filled unless `filled: false`. `size` is in pixels.
- **Images**: `position` is the top-left corner. `width` or `height` alone can only shrink.
- **Numbers**: the integration parses every value, even plain text: `content: "11.10"` shows `11.1`, `"+5"` shows `5`. Keep a unit or other text in the same `content`. Where templates are rendered: [pages](references/pages.md#where-templates-are-rendered).

## Fonts

`suggest` picks the font; [fonts](references/fonts.md#choosing-a-font) explains its choice and how to override it. Three defaults when you cannot run the tools: `tiny5` for text, `pico_8` for small numbers that change, `eleven_pix` for a big value.

## References

| Read | When |
|---|---|
| [pages](references/pages.md) | Before you use an image, rectangle, `templatable`, a built-in page, or templates in `pages_data` |
| [layout](references/layout.md) | When you place text by hand, override `suggest`, mix fonts, template text that may wrap, or pick colors |
| [fonts](references/fonts.md) | When you need font metrics, glyph coverage, or the reasons behind a font choice |
| [operations](references/operations.md) | Before step 7, before writing a reusable script, and when the device is offline or slow |
| [custom fonts](references/custom-fonts.md) | When adding a `.bdf` file |
| [troubleshooting](references/troubleshooting.md) | When the device shows something other than `render` predicted |
| [changes](references/changes.md) | When migrating pages written for 1.23 or earlier |
| [checklist](references/checklist.md) | At step 8, and when reviewing someone else's Pixoo automation |
| [design](references/design.md) | When the user wants a theme, an icon, a nicer look, or ideas for a page |
| [lessons](references/lessons.md) | When reviewing or fixing existing Pixoo pages: the mistakes real configurations make |

## Examples

Tested pages to copy before step 2: [notification](examples/notification.yaml), [sensor value with a minus sign](examples/sensor-value.yaml), [status list](examples/status-list.yaml), [alarm with a bell icon](examples/alarm-bell.yaml), [image with a label](examples/image-with-label.yaml), [progress bar](examples/progress.yaml), [device pages: clock, channel, visualizer, gif](examples/device-pages.yaml), [device calibration](examples/calibration.yaml). Icons for `sprite`: [examples/sprites](examples/sprites/).
