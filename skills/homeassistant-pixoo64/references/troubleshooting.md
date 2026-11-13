# Troubleshooting

Start with `pixoo.py render` on the page: most text problems show up there. Then check the Home Assistant log for `divoom_pixoo`.

| Symptom | Likely cause | Fix |
|---|---|---|
| Text cut off at the sides | Line wider than 64 px (no wrapping) | `suggest` a font or wrap; `measure` shows the width |
| Top row of text missing (i-dots, accents) | BDF font draws above y and y is too small | Raise y (Tiny5: 1, with accented capitals 7) |
| `?` in the text | Character not in a BDF font | `coverage`; choose `tiny5` or `pixelifysans`, or change the text |
| A character silently gone, text a bit off-center | Character not in a matrix font (`-` in `pix24`, `%` in `eleven_pix`) | `coverage`; see [layout](layout.md#symbols-a-font-lacks) |
| A gap where an accented letter should be | `pico_8` has empty accented glyphs | Use `tiny5` |
| Lower case where capitals were expected (after updating to 1.24.0) | 1.24.0 no longer uppercases | `content: "{{ text \| upper }}"` or type capitals |
| Lower case shown as capitals | `gicko`, `eleven_pix` have no lower case; `five_pix` lower case is a copy of its capitals | Use `tiny5`, `tiny5duo`, `pixelifysans` or `pressstart2p` |
| Small capitals instead of lower case | That is how `pico_8` draws lower case | Use `tiny5` |
| Text white instead of the color asked | Color name not lower-case CSS4, or a hex string | `[R, G, B]` or a lower-case name |
| Number shows `11.1` instead of `11.10` | Native template types | Keep a unit or text in the same `content` |
| `Template Error` on the display | The content template failed | Test it with `ha_eval_template` / Developer Tools |
| Font looks like pico_8, log says "Unknown font" | Wrong name, `font_` in a file name, or a broken BDF | `pixoo.py --config /config doctor` |
| New font file not found | Folder scanned only at setup | Reload the integration entry; restart after changing a used file |
| Rectangle is a solid block | `filled` defaults to true | `filled: false` |
| Image does not get bigger | `width` or `height` alone only shrinks | Set both, or scale the file |
| `visualiser` page does nothing | Only `visualizer` is accepted | Fix the spelling |
| `progress_bar` or `pv` page not drawn | `progress` not an integer, or a `pv` value is `unavailable` | `| int(0)`, `| float(0)` |
| Message disappears after a few seconds | Rotation resumes after `duration` | Pass the `duration` you want |
| Message never goes away | No rotation pages, so nothing replaces it | Send another page or turn the screen off |
| Automation stops with a connection error | Device offline; `show_message` raises a raw connection error that `continue_on_error` cannot catch | Check the sensor is not `unavailable` first, and start Pixoo work with `script.turn_on` so a failure stops only that script |
| Setup says "Unable to connect" on a new Pixoo 64 II | New firmware API format | Known open issue #163; not fixed by the 1.24.0 fallback |
| Device stops answering after hours, ping still works | Device-side hang (#153) | `divoom_pixoo.restart` or a power cycle; send fewer updates |
| Right-aligned text 1 px left of where it was before 1.24.0 | BDF advance includes trailing space (#162) | Add 1 to x (`measure` prints the value) |
| Page rotation stopped | All rotation pages disabled (#167) | Enable one page and reload the integration |
