# Layout on the 64 x 64 grid

How the integration places text, and how to place it on purpose. `measure` and `suggest` do all of this math; use this page to understand their output or to place things by hand.

## Contents

- [The grid](#the-grid)
- [Horizontal alignment](#horizontal-alignment)
- [Vertical placement](#vertical-placement)
- [Several lines](#several-lines)
- [Mixing fonts](#mixing-fonts)
- [Values that change](#values-that-change)
- [Templated text](#templated-text)
- [Symbols a font lacks](#symbols-a-font-lacks)
- [Color on LEDs](#color-on-leds)
- [Layout recipes](#layout-recipes)

## The grid

- Columns `x` 0-63 left to right, rows `y` 0-63 top to bottom. Pixels outside are dropped without a message.
- The center falls between columns 31 and 32 and between rows 31 and 32. Ink that spans an even number of columns can be exactly centered; an odd number is always 1 px off.
- The page starts black (all LEDs off). Components paint in list order: later ones cover earlier ones.
- Keep 1 px of margin at the left and right edges (`suggest --margin 1`, the default). Text that touches the edge looks cut off even when it is not.

## Horizontal alignment

The integration computes a pen start per line from the **advance width** (not the ink):

| `align` | Pen start | Typical result |
|---|---|---|
| `left` (default; also any unknown value) | `x` | Ink starts at `x` (PixelifySans: `x+1`) |
| `center` | `x - int(width / 2)` | Ink center is 0 to 1.5 px left of `x`, by font and text |
| `right` | `x - width` | Matrix fonts: ink ends at `x-1`. Most BDF fonts: `x-2` |

Width: matrix fonts = sum of glyph widths + 1 px per gap. BDF fonts = sum of advances, and each advance includes the blank column after the glyph.

Practical rules:

- Center on the full display with `x: 32`, then check the margins `measure` prints. It suggests a better x when the left and right margins differ by 2 px or more. `suggest` already picks that x.
- To end right-aligned ink at the right edge (column 63): matrix fonts `x: 64`, most BDF fonts `x: 65`, PixelifySans `x: 64`. `measure` prints the exact value.
- Each line of a multi-line text is aligned on its own.

## Vertical placement

`position` y is the **cap line**: the top row of a capital letter or digit.

| Font | Baseline row | ASCII ink rows | Line height |
|---|---|---|---|
| `pico_8`, `five_pix` | 4 | 0 to 4 | 6 |
| `tiny5`, `tiny5duo` | 4 | -1 to 5 | 9 |
| `gicko` | 5 | 0 to 5 | 7 |
| `pixelifysans` | 6 | -1 to 8 | 13 |
| `pressstart2p` | 6 | 0 to 7 | 8 |
| `eleven_pix` | 10 | 0 to 10 | 12 |
| `clock` | 11 | 0 to 11 | 13 |
| `pix24` | 23 | 0 to 23 | 25 |

Accented capitals go higher: Tiny5 up to row -7, PixelifySans row -4. Rows are relative to y.

- **Top edge**: y must be at least minus the top ink row (Tiny5: y >= 1; with accented capitals y >= 7).
- **Bottom edge**: y + bottom ink row must be 63 or less. `pico_8` at y = 59 ends at row 63.
- **Center in a box** `(top, height)`: `y = top + (height - ink_height) // 2 - ink_top`. Use the real ink of the text for fixed text, and the font's ASCII extents (`suggest --stable`) for templated text, so the line does not jump when a descender appears.
- **Optical center**: for text in capitals, center the capitals and ignore the descender rows; the eye reads that as centered.

## Several lines

- A `\n` in `content` moves down by the line height. In YAML, write `"line one\nline two"` in double quotes, or a `|-` block.
- One component per line gives you control of the gap; one component with `\n` gives the font's own spacing. PressStart2P lines touch (no blank row), so use separate components 9-10 px apart.
- Balance the lines: `suggest` and `wrap` pick the fewest lines, then the most even widths ("Someone is at / the front door", not "Someone is at the / front door").
- Words wider than the box cannot wrap. Choose a narrower font, shorten the word, or `suggest --hyphenate`.

## Mixing fonts

Pick one of two alignments and keep it for the whole page:

- **Cap lines aligned**: give both components the same y. Their tops line up. Good for a label beside an icon or a square.
- **Baselines aligned**: `y_small = y_big + baseline_big - baseline_small` (baselines from the table above). Good for a value and its unit: `eleven_pix` at y=20 has its baseline at row 30; `tiny5` at y = 20 + 10 - 4 = 26 ends on the same row.

Keep at least 1 blank row between components. `render` warns when ink of two texts touches, and fails when it overlaps.

## Values that change

- Use a font with same-width digits (`pico_8`, `tiny5`, `tiny5duo`, `eleven_pix`, `pressstart2p`, `clock`). With other fonts, right-align the value at a fixed x so it grows to the left and the unit stays still.
- Size the slot for the worst case: `budget --width 30 --pattern=-88.8` tells you if `-88.8` fits in 30 px in each font.
- Keep a unit or other text in the same `content` as a number (`"{{ '%.1f' | format(x) }}°"`). When the whole output looks like a number, Home Assistant's native types turn it back into a number and drop trailing zeros (`11.10` shows `11.1`, issue #133), even if you formatted it.
- `states()` can return `unavailable` or `unknown`: use `| float(0)` or show a dash, and make sure the dash is in the font.

## Templated text

Names, titles and weather words change length. Give them a slot with a fixed number of lines, and check the worst case.

1. Pick the font and the slot with `suggest` on a long sample, then get the characters per line from `budget --font F --width W` (use the `upper` worst case for capitals or unknown text, `lower` typical for ordinary words).
2. Wrap in the template with Jinja's `wordwrap`, which counts characters, and cap the line count:

   ```yaml
   - variables:
       lines: "{{ (trigger.to_state.name | wordwrap(10, true, '\n')).split('\n')[:2] }}"
   - action: divoom_pixoo.show_message
     data:
       page_data:
         page_type: components
         components:
           - type: text
             content: "{{ lines | join('\n') }}"
             font: tiny5
             align: center
             position: [32, "{{ 20 if lines | count > 1 else 24 }}"]   # center 1 or 2 lines in the slot
   ```

   A templated `position` works in a `show_message` call (Home Assistant renders it first), not in `pages_data`. Words past the line cap are dropped (`Wohnzimmerfenster links` becomes `Wohnzimmer` / `fenster`); tell the user, or shorten names first.
3. Check every case: `render FILE --fill "0=WWWWWWWWWW\nWWWWWWWWWW" --fill 0.position=32,20`, then a one-line sample with `0.position=32,24`.

When the exact pixel width matters at run time (a minus sign beside a number, a unit after a value), compute it in the template: `pixoo.py jinja --font F --chars "0123456789.°" --var t` prints a snippet that adds up the glyph advances exactly as the integration does. The [sensor value](../examples/sensor-value.yaml) example uses it.

`show_message` renders the templates once, when it is called: a time or a value on the page does not update while it shows. For a live clock use a `clock` page, or send the page again every minute.

## Symbols a font lacks

| Need | Way |
|---|---|
| Minus in `pix24` or `eleven_pix` | A filled rectangle (`pix24`: 6 x 3; `eleven_pix`: about 5 x 2, check with `render`) left of the number; template its color to black when the value is not negative. See [sensor value](../examples/sensor-value.yaml). |
| `%`, `+` with `eleven_pix` | A second text component in `tiny5` or `pixelifysans`, baseline-aligned. |
| Arrows | `tiny5`, `tiny5duo`, `pressstart2p` or `pico_8` have `← → ↑ ↓`. |
| Icons, emoji, ✓ | An `image` component (8 x 8 or 16 x 16 PNG, `resample_mode: nearest`). |
| Accented names | `tiny5`, `tiny5duo`, `pixelifysans` or `pressstart2p`, the fonts that draw accents. (`pico_8` has the code points but empty glyphs.) |

## Color on LEDs

- Black is "off": the best contrast, the least heat. Light text on black reads best.
- Pure blue `[0, 0, 255]`, `navy`, `darkblue` and `purple` are dim on LEDs and hard to read on black (contrast about 2:1). Use `dodgerblue`, `deepskyblue` or `lightskyblue`. `render` warns below 3:1.
- At low brightness, dark colors can drop out (suggestion, not measured). Prefer channel values of 80 or more for text.
- Text over an image: `render` cannot judge the contrast. Look at the PNG, or put a dark filled rectangle behind the text.
- Color names must be lower-case CSS4 names (`lightskyblue`, `darkslateblue`, `gray`). Anything else becomes white (or the page default) without an error.

## Layout recipes

Boxes to start from. Run `suggest TEXT --box x,y,w,h` in each.

| Layout | Boxes |
|---|---|
| Title bar + body + footer | bar: rectangle 0,0,64,11 + text box 0,0,64,11; body 0,13,64,36; footer 0,56,64,8 |
| Big value + label | label 0,0,64,10; value 0,12,64,30; second line 0,46,64,16 |
| Three status rows | square 5 x 5 at x=4; label box 12,y,51,9; rows at y = 17, 30, 43 (see [status list](../examples/status-list.yaml)) |
| Two by two values | cells 0,0,32,32 / 32,0,32,32 / 0,32,32,32 / 32,32,32,32; each: label 6-9 rows, value below |
| Icon + text | image 16 x 16 at 2,2; text box 20,2,43,16 |
