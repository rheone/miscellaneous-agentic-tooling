# Adding your own BDF font

1.24.0 loads any BDF (Bitmap Distribution Format) font file you put in a font folder. Use this for a pixel font with glyphs the bundled ones lack, or a different size.

## Where the integration looks

Scanned once when the integration sets up, in this order. A later folder wins when two files have the same name.

1. `custom_components/divoom_pixoo/fonts/` (bundled; replaced by updates, so never put your files here)
2. `<config>/fonts/`
3. `<config>/esphome/fonts/` (shared with ESPHome)

- Only files ending `.bdf` directly in the folder count (no subfolders).
- The YAML name is the file name without `.bdf`, case-insensitive: `/config/fonts/Spleen6x12.bdf` is `font: spleen6x12`.
- A file named like a bundled font replaces it (`/config/fonts/PICO_8.bdf` changes every `pico_8` text, also in the `progress_bar`, `fuel` and `pv` pages).
- **Name the file without the text `font_`.** The lookup deletes `font_` from the requested name, so `My_font_big.bdf` can never be found and draws `pico_8`. `doctor` flags such files.
- A file is parsed the first time a page uses it and then kept in memory. A **new** file name needs a reload of the integration entry. A Home Assistant restart is needed when you change a file that was already used, or add a file that replaces a font name already used (the loaded font stays cached).
- A file that cannot be parsed logs a warning; its name then draws `pico_8`.

## Make or get a BDF

- Prefer a font drawn as pixels at the size you want (many are BDF already: Spleen, Terminus, Cozette, the X11 misc-fixed fonts, u8g2's font sources). Check the license before you copy it.
- From a pixel TTF/OTF made on a grid: convert at its native pixel size, for example with FontForge (Element > Bitmap Strikes, then File > Generate Fonts > BDF) or `otf2bdf -p <pixels> -r 72 font.ttf -o font.bdf`. A vector font converted to 5-8 px looks blurry and uneven; that is a design limit, not a conversion error.
- Each glyph needs `ENCODING` (the Unicode code point). Glyphs without it are only found by a `STARTCHAR` name like `U+00E9`, `uni00E9` or a single character.

## What the integration reads from the file

| BDF item | Used for |
|---|---|
| `DWIDTH` per glyph (else the font's `DWIDTH`, else the bounding-box width) | Advance. Include 1 px of space in it, as the bundled fonts do. |
| `BBX w h xoff yoff` | Where the bitmap sits relative to the baseline. |
| `CAP_HEIGHT` property | Puts the baseline at row `CAP_HEIGHT - 1`, so capitals start at y. Without it, the baseline comes from the `A` glyph, then `0`, then `FONT_ASCENT - 1`. Add `CAP_HEIGHT` if your capitals sit at the wrong height. |
| `FONT_ASCENT + FONT_DESCENT` | Line height for `\n`. |
| `?` glyph | Drawn for missing characters. Without it, missing characters draw nothing and take 3 px. |
| space glyph | Width of a space (else 2 px). |

## Check it before you use it

Point the tools at your config folder so they scan the same font folders:

```
python -I tools/pixoo.py --config /config doctor            # is the file found, under which name?
python -I tools/pixoo.py --config /config font myfont        # metrics, notes, blank glyphs
python -I tools/pixoo.py --config /config coverage "ÄÖÜ°%€" --font myfont
python -I tools/pixoo.py --config /config specimen "Hxgy 0123" --font myfont
```

Check in the output: the capital top is row 0 (`capitals rows 0..N`), the line height leaves a blank row, and every character you need is `ok`. Then add the font to a page and run `render`.

Large fonts cost memory: Tiny5 is 166 KB on disk with 1654 glyphs. Strip glyphs you will never use if the file is several MB.
