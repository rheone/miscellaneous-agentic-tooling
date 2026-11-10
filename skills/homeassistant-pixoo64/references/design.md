# Themes and design ideas

Ideas for pages that look designed rather than typed. Each theme lists fonts and colors whose contrast was checked with the tool's 3:1 rule (numbers are contrast against the theme background). Build every page with the normal workflow; these are starting points for step 2.

## Contents

- [Principles for 64 x 64](#principles-for-64-x-64)
- [Themes](#themes)
- [Techniques](#techniques)
- [Page ideas](#page-ideas)
- [Asking for designs](#asking-for-designs)

## Principles for 64 x 64

- **One message per page.** One big thing (a value, an icon, a word), at most two small things. A second idea gets a second page.
- **Hierarchy by size, then color.** The most important item uses the biggest font that fits; secondary text is 5 px in a quieter color.
- **Color carries meaning.** Use one accent color for state (green ok, amber warning, red alarm) and keep the rest neutral. Keep the meaning the same on every page.
- **Black is part of the design.** Unlit LEDs are the darkest, crispest background. Full-screen color backgrounds glow and lower contrast.
- **Grid.** Keep a 1-2 px margin and line items up on the same x. Use cap-line or baseline alignment ([layout](layout.md#mixing-fonts)).

## Themes

| Theme | Fonts | Background | Colors (contrast) | Use for |
|---|---|---|---|---|
| Arcade | `pressstart2p` titles, `pico_8` small | black | `yellow` 19.6, `cyan` 16.7, `lime` 15.3, `magenta` 6.7, `orangered` 6.1 | Games, achievements, printer done, "level up" moments |
| Terminal | `pico_8` throughout | black | `lime` 15.3, `springgreen` 15.6, `limegreen` 9.9 (avoid `darkgreen` 2.8) | Server and network status, logs, Proxmox |
| Night | `clock` or `tiny5duo`, few items | black | `red` 5.3, `firebrick` 3.1 (avoid `darkred` 2.1 and dim custom reds) | Bedroom hours, low brightness |
| Nordic | `pixelifysans` titles, `tiny5` text | `midnightblue` rectangle | `white` 14.8, `gold` 10.6, `lightgray` 9.9, `lightskyblue` 8.7 | Weather, calendar, calm information |
| Sunset | `pixelifysans`, `tiny5` | black | `gold` 15.0, `orange` 10.6, `hotpink` 7.9, `tomato` 7.1, `mediumpurple` 5.6 | Golden hour, sunrise and sunset, evening scenes |
| Neon | `tiny5duo`, `eleven_pix` | `[10, 10, 40]` | `yellow` 18.0, `aqua` 15.4, `deeppink` 5.3 | Media now playing, parties |
| Paper | `pixelifysans`, `tiny5` | `oldlace` rectangle | `black` 19.4, `navy` 14.8, `darkslategray` 8.2, `firebrick` 6.2 | Reminders and to-dos that should feel like a note (bright: test at night) |

Check a theme of your own: put the colors on a test page and `render` it; the `contrast` warning flags pairs under 3:1.

## Techniques

- **Icons without image files.** Draw pixel art as text (`#` = pixel, other letters = other colors) and convert it: `pixoo.py sprite art.txt --x 18 --y 2 --scale 2 --palette "#=gold,o=lightyellow"`. It merges pixels into as few rectangles as it can. See [examples/sprites](../examples/sprites/) and the [alarm page](../examples/alarm-bell.yaml). Keep icons 8-16 art pixels; `--scale 2` doubles them for distance.
- **Templated sprite colors.** Give each rectangle a color template to show state (a bell that is gold when ringing and gray when snoozed).
- **Bars and gauges.** A gray rectangle as the track and a colored one whose `size` width is a template (`{{ (value / 100 * 60) | int }}`). Rectangle size and position are templates even in `pages_data`.
- **Frames and badges.** An outline rectangle (`filled: false`) around a value, or a filled rounded look: a filled rectangle with the four corner pixels drawn in the background color.
- **Two-tone text.** Draw the same text twice, 1 px apart, in a dark and a bright color for a drop shadow. Check with `render` that the shadow does not touch other items.
- **Motion.** The integration sends still frames. Use a `gif` page for animation, or alternate two pages in the rotation (`pages_data`) for a slow blink. For an alarm, a short series of `show_message` calls a few seconds apart can swap a "bell left" and a "bell right" sprite; keep the rate low (see [operations](operations.md#rate-and-stability)).
- **Text that fits any value.** Combine `budget` (slot size), `wordwrap` (line breaks) and `jinja` (exact widths) as in [layout](layout.md#templated-text).

## Page ideas

| Idea | Build |
|---|---|
| Alarm or timer | Bell sprite, time in `clock`, title in `pixelifysans` ([example](../examples/alarm-bell.yaml)). Ringing: gold bell, swap a tilted bell every few seconds. |
| Weather glance | Sun or cloud sprite top-left, temperature in `eleven_pix` right-aligned, condition word in `tiny5` below. Map condition slugs to short words first. |
| Printer progress | Arcade theme: title in `pressstart2p`, a bar from rectangles, percent in `pico_8`, end time in `clock`. |
| Door and window board | Status list with one square per opening, red only when open ([example](../examples/status-list.yaml)). |
| Air quality | Big value in `eleven_pix`, unit `ppm` and `CO₂` in `tiny5` (only Tiny5, Tiny5Duo and PixelifySans have `₂`), a bar colored by level. |
| Now playing | Neon theme: artist in `tiny5duo`, title wrapped to two lines in `tiny5`, a thin progress bar. |
| Night clock | Night theme at low brightness: time in `clock` in `red`, nothing else. |
| Countdown | Days left in `pix24`, event name in `tiny5`, a ring of dots made of 1-pixel rectangles that empties as the day nears. |

## Asking for designs

Prompts that work well with this skill:

- "Show the outdoor temperature on the Pixoo, readable from the sofa, in the Nordic theme."
- "Design an alarm page with a bell icon; show me the preview before you send it."
- "Lint all my Pixoo automations and fix the ones that overflow."
- "Make a 12 x 12 pixel-art cat icon for the feeding reminder."
- "Which font can show `Tormenta eléctrica` in two lines?"
