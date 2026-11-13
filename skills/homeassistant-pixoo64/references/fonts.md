# Fonts in divoom_pixoo 1.24.0

All numbers here come from `pixoo.py --vendored fonts` and `coverage`. They are a snapshot of 1.24.0. When `pixoo.py` prints a drift warning, run the commands again and trust their output over this page.

## Contents

- [Anatomy: the words used here](#anatomy-the-words-used-here)
- [The two font engines](#the-two-font-engines)
- [Metrics of every font](#metrics-of-every-font)
- [Font profiles](#font-profiles)
- [Symbol coverage](#symbol-coverage)
- [Choosing a font](#choosing-a-font)

## Anatomy: the words used here

Rows are counted from the `y` of the text component. Row 0 is where the integration puts the top of a capital letter.

```
             tiny5 "Hxgy"            pico_8 "Hxgy"
row  0  y    #..#............         #.#............    <- cap line: top of capitals (= position y)
row  1 x-ht  #..#.#.#..##.#.#         #.#.#.#..##.#.#    <- x-height: top of lower case
row  2       ####..#..#.#.#.#         ###..#..#...###
row  3       #..#.#.#.#.#.#.#         #.#..#..#.#...#
row  4 base  #..#.#.#..##..#.         #.#.#.#.###.##.    <- baseline: bottom of capitals
row  5       .........##..#..                            <- descender (g, y) below the baseline
```

| Term | Meaning on the Pixoo |
|---|---|
| Cap height | Rows a capital or digit uses. The main measure of size. |
| x-height | Rows a lower-case `x` uses. Small x-height with no ascenders = small capitals. |
| Descender | Rows below the baseline used by `g j p q y`. Only Tiny5, Tiny5Duo, PixelifySans and PressStart2P have them. |
| Ink above y | Rows above row 0: i-dots, accents, some punctuation. Clipped when y is too small. |
| Advance | How far the pen moves after a glyph, including its built-in space. |
| Side bearing | Blank columns inside the advance. PixelifySans starts every glyph 1 px right of the pen. |
| Tracking | Extra space between letters. Matrix fonts add 1 px; BDF fonts add none (it is in the advance). |
| Line height | How far `\n` moves down. Not the same as cap height: Tiny5 is 5 px tall on 9 px lines. |
| Tabular digits | All ten digits have one advance. A changing number then keeps its width. |
| Ink box | The rectangle the lit pixels really cover. `measure` reports it; alignment uses the advance width instead. |
| Glyph status | `ok`, `case-fallback` (drawn as the capital), `typography-fallback` (`’` drawn as `'`), `missing`, `blank` (code point exists, glyph is empty). |

## The two font engines

| | Matrix fonts | BDF fonts |
|---|---|---|
| Fonts | `gicko`, `five_pix`, `eleven_pix`, `clock`, `pix24` | `pico_8`, `tiny5`, `tiny5duo`, `pixelifysans`, `pressstart2p`, any user file |
| Source | Bit lists in `pixoo64/_font.py` | `.bdf` files, parsed on first use |
| Width of text | sum of glyph widths + 1 px per gap | sum of advances (trailing space included) |
| Vertical | glyph top at y | capital top at y, ink can go above and below |
| Missing glyph | draws nothing, but adds 1 px to the width used for alignment | draws `?` (3 px if the font has no `?`) |
| Lower case | from the capital (`five_pix` has lower-case glyphs, but they copy the capitals) | own glyphs (pico_8: small capitals) |
| Right align | ink ends at x-1 | ink usually ends at x-2: the advance includes the space after the glyph (issue #162). PixelifySans ends at x-1. |

`pico_8` is both: the matrix version is built in, but the bundled `PICO_8.bdf` replaces it on first use. Only the BDF is ever drawn, unless the file fails to load.

Font names are case-insensitive. `FONT_GICKO`, `gicko` and `Gicko` are the same. `pico-8` finds `pico_8`. An unknown name logs a warning and draws with `pico_8`.

## Metrics of every font

| Font | Engine | Line | Cap | x-ht | Desc | Top row | Lower case | Same-width digits | Per line `0`/`A`/`a` |
|---|---|---|---|---|---|---|---|---|---|
| `pico_8` | BDF | 6 | 5 | 4 | 0 | 0 | small caps | yes (4) | 16/16/16 |
| `tiny5` | BDF | 9 | 5 | 4 | 1 | -1 (any glyph -7) | yes | yes (4) | 16/12/16 |
| `tiny5duo` | BDF | 9 | 5 | 4 | 1 | -1 (any glyph -7) | yes | yes (6) | 10/10/10 |
| `pixelifysans` | BDF | 13 | 7 | 5 | 2 | -1 (any glyph -4) | yes | no (4-6) | 10/10/9 |
| `pressstart2p` | BDF | 8 | 7 | 5 | 1 | 0 | yes | yes (8) | 8/8/8 |
| `five_pix` | matrix | 6 | 5 | - | 0 | 0 | as capitals | no (4-6) | 13/13/13 |
| `gicko` | matrix | 7 | 6 | - | 0 | 0 | as capitals | no (5-7) | 9/9/9 |
| `eleven_pix` | matrix | 12 | 11 | - | 0 | 0 | as capitals | yes (7) | 9/9/9 |
| `clock` | matrix | 13 | 12 | - | 0 | 0 | none | yes (7) | 9/-/- |
| `pix24` | matrix | 25 | 24 | - | 0 | 0 | none | no (8-11) | 6/-/- |

"Per line" is how many copies fit in 64 px. Real text varies: `tiny5` fits 10 `M` but 32 `i`.

## Font profiles

### `tiny5` (Tiny5, OFL)

The best general font. 5 px capitals, real lower case with 1 px descenders, 4 px digits that never shift, and 1654 glyphs: Latin accents, Greek, Cyrillic, arrows `← → ↑ ↓`, `€ £ µ ² ³ ± × ÷`. Lines are 9 px, so three lines fit in 27 rows. **Watch**: `i`, `j` and the backtick draw at row -1, accented capitals up to row -7. At the top edge, keep y at 1 or more (7 for accented capitals).

### `tiny5duo` (Tiny5 Duo, OFL)

Tiny5 drawn with 2 px vertical strokes: the same height, about 1.5 times as wide (6 px digits). Suggestion, not tested on a device: the heavier strokes should read better from a distance and at low brightness. Same coverage and the same ink-above-y rule as Tiny5.

### `pico_8` (PICO-8, CC0)

Every letter, digit and ASCII sign has a 4 px advance (arrows 5 px, symbols such as `♥ ★` 8 px), so it is the most predictable font: 16 characters per line, and a changing value never moves. Lower case is small capitals (4 px). It has `+ / ( ) & @ # $` and arrows, but no accents: 27 accented capitals (`À` to `Ù`, `É`) and `×` exist but are **empty** and draw a gap; lower-case accents fall back to those empty capitals. No `€ £ µ ² ³`. Right-aligned ink ends at x-2.

### `pixelifysans` (Pixelify Sans, OFL)

The largest font with real lower case: 7 px capitals, 2 px descenders, 13 px lines. Good for titles. Proportional digits (`1` is narrower), so put changing values in another font or right-align them. Every glyph starts 1 px right of the pen. `` $ ( ^ ` { } `` reach row -1 (its i-dot does not), accents row -4. Has accents, Greek, Cyrillic, `€ £ µ ² ³ ± × ÷ …`; no arrows (`↑ ↓` become `^ v`).

### `pressstart2p` (Press Start 2P, renamed "Pixoo Retro 2P", OFL)

8 x 8 arcade monospace: exactly 8 characters per line, 7 px capitals. The line height (8) equals the ink height with descenders, so two lines touch. For more than one line, use two components 9-10 px apart. Widest coverage of symbols after Tiny5, including arrows and `♥`. The YAML name is the file name `pressstart2p`; "Pixoo Retro 2P" is not a lookup name.

### `five_pix` (matrix)

5 px capitals. It has lower-case glyphs, but each one is a copy of its capital, so mixed-case text looks all capitals (confirmed on the device, 2026-11-08). 13 digits per line, proportional. Coverage is thin: `° % - ! ? : . ,` and nothing else. Used by the `progress_bar` and `fuel` pages.

### `gicko` (matrix)

Bold 6 px capitals and digits; lower case is drawn as capitals. `° % - ! ? : .` only; no `/ , ' + ( )`. Good for short labels and headers in capitals.

### `eleven_pix` (matrix)

11 px capitals and same-width 7 px digits: the best big font for values that change. Lower case drawn as capitals. Only `. : ? °`: **no `-`, `+`, `%`, `!`, `/`**. Draw a minus or a percent sign another way (see [layout](layout.md#symbols-a-font-lacks)).

### `clock` (matrix)

6 x 12 monospace digits, `:`, `.`, `?` and `C`. Nothing else. Each character is 7 px, so `HH:MM` is 34 px.

### `pix24` (matrix)

24 px digits, `° % , . : ?` and `C`. No letters, no minus. Digits differ in width (8-11 px). Fits about 5 digits per line.

## Symbol coverage

`ok` = drawn from its own glyph. `~` = drawn as an ASCII stand-in. `--` = missing. `__` = empty glyph (gap).

| Font | ° | % | + | - | ! | / | , | ' | ( | € | µ | ² | × | · | … | → | ↑ | ♥ | ✓ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `pico_8` | ok | ok | ok | ok | ok | ok | ok | ok | ok | -- | -- | -- | __ | -- | ok | ok | ok | ok | -- |
| `tiny5`, `tiny5duo` | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | -- | -- |
| `pixelifysans` | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | -- | ~ | -- | -- |
| `pressstart2p` | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | -- |
| `five_pix` | ok | ok | -- | ok | ok | -- | ok | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| `gicko` | ok | ok | -- | ok | ok | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| `eleven_pix` | ok | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| `pix24` | ok | ok | -- | -- | -- | -- | ok | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| `clock` | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |

No bundled font has emoji, `✓` or `☀`; `★` and `♥` are in `pico_8` and `pressstart2p`. Use an image component for icons.

Typography stand-ins: `’ ‘` become `'`, `“ ”` become `"`, `— –` become `-`, `↑` `^`, `↓` `v`, but only when the font has the stand-in and not the original. `…` and `→ ←` have multi-character stand-ins (`...`, `->`) that the code can never use: in a font without them they are missing.

## Choosing a font

Run `suggest`; it applies these rules and shows its reasons. Use this section to understand or override its choice.

1. **Coverage first.** A font that cannot draw a character is out, whatever its size. For text you do not control (titles, names, weather words), prefer `tiny5`, `pressstart2p` or `pixelifysans`, which cover accents and most symbols.
2. **Then size by role.**
   - Value that changes (temperature, count, price): the largest font with same-width digits that fits: `eleven_pix`, then `pressstart2p`, `tiny5duo`, `tiny5`, `pico_8`. With `pix24`, right-align so the value grows to the left.
   - Headline: the largest that fits on one or two lines: `pixelifysans` (mixed case), `eleven_pix` or `gicko` (capitals).
   - Body text: `tiny5` (mixed case); `pico_8` when you need 16 characters per line; `five_pix` for a compact matrix look in capitals.
   - Label next to something: 5 px fonts (`tiny5`, `five_pix`, `pico_8`).
   - Time: `clock` for big, `pico_8` for small.
3. **Case.** If lower case carries meaning (names, units like `mA` vs `MA`), use a font with real lower case (`suggest --keep-case`).
4. **Templated text.** Size for the worst case: `budget --width W --pattern=-88.8°F`. Place with `suggest SAMPLE --stable`.
5. **Mixing.** Use at most two fonts per page, three with a large number. Align their cap lines or baselines (see [layout](layout.md)).
6. **Distance.** At 2 m or more, 5 px fonts are hard to read; use `tiny5duo` or 7 px and larger.
