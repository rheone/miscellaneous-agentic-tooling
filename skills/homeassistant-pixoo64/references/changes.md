# What changed in 1.24.0, and corrections to older guidance

Release "1.24.0 – BDF Fonts & Pixoo API Fallback", published 2026-09-30. Tag `1.24.0` (no `v`). Source: https://github.com/gickowtf/pixoo-homeassistant/releases/tag/1.24.0

## Changes that affect existing pages

1. **Text is no longer uppercased.** Lower case now shows: as small capitals in `pico_8`, as real lower case in the new BDF fonts, and as capitals in `gicko`, `eleven_pix` and `five_pix` (the release note says `five_pix` uses its lower-case glyphs; they are copies of its capitals, confirmed on the device 2026-11-08). This also reaches the `fuel` names and `progress_bar` header and footer. Use `| upper` to keep the old look.
2. **`pico_8` is now the bundled `PICO_8.bdf`**, not the built-in bitmap. Every glyph is 4 px wide (16 per line), and right-aligned text ends 1 px further left (#162).
3. **Missing characters in matrix fonts draw nothing** (before: `?` and a log error). BDF fonts draw `?`.
4. **Unknown font names log a warning** and use `pico_8`. Font names are case-insensitive; `FONT_` prefixes still work.
5. **New fonts**: `tiny5`, `tiny5duo`, `pixelifysans`, `pressstart2p`, plus any `.bdf` in `<config>/fonts` or `<config>/esphome/fonts`.
6. **Port 9000 fallback** for the device API. It does not fix the Pixoo 64 II (#163, #168).
7. Unchanged: services, page types, component types, config flow.

Earlier releases: 1.23.0 (2026-03-20) added `pix24`; 1.22.0 (2026-03-15) made the `clock`, `channel`, `visualizer` ids and `gif_url` templates; 1.21.0 (2026-03-07) fixed the light for Home Assistant 2026.3.

## Not included

Component animations and hosted GIFs (PRs #157, #158) were held back. There is still no scrolling text, no text background, no hex colors and no per-page brightness.

## Corrections to skill version 1.0.2

| It said | 1.24.0 does |
|---|---|
| All text is rendered UPPERCASE | Text is drawn as given |
| Rectangle `filled` defaults to false | Defaults to **true** |
| `visualiser` is accepted | Only `visualizer` |
| Images take `align: center` | `align` is ignored; `position` is the top-left corner |
| `width`/`height` set the longest side | One alone only shrinks (never enlarges); both stretch to exactly that size |
| Chars per line: pico_8 ~12, gicko ~8, five_pix ~16, eleven_pix ~7, clock ~6, pix24 ~4 | 16, 9, 13, 9, 9, 6 for digits; letters vary (see [fonts](fonts.md)) |
| `clock` font draws `[0-9:]` | Also `.`, `?`, `C` |
| Unknown characters show as `?` | Only in BDF fonts; matrix fonts draw nothing |
| Wake, show, delay, then always turn off | Turn off only if the screen was off before; send the page before turning the screen on |
| `duration` is how long the message shows | Only when rotation pages exist; otherwise the page stays |
| Color presets: any name | Lower-case CSS4 names only; others become white |
| Six fonts | Ten bundled, plus your own |
