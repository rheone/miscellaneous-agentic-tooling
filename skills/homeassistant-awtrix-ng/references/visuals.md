# Names and looks

The four name lists are separate and case-insensitive. `Ripple` and `Fade` are both an effect and a transition, and look different. An unknown name rejects the payload. The clock lists valid names on the retained `<P>/state/capabilities` topic.

## Background effects (`effect`)

Behind text and icons. Set per app.

| Effect | Look | Palette |
|---|---|---|
| `Plasma` | Flowing plasma | yes |
| `PlasmaCloud` | Soft drifting clouds | yes |
| `Pacifica` | Ocean waves, blue-teal by default | yes |
| `ColorWaves` | Colors spread once, sliding sideways | yes |
| `TwinklingStars` | Stars that flare and fade | yes |
| `Fireworks` | Rockets and sparks | yes |
| `Ripple` | Rings from random points | yes |
| `Radar` | Sweeping beam, green by default | yes |
| `Fade` | Horizontal bands cycling color | yes |
| `MovingLine` | Line bouncing up and down | yes |
| `TheaterChase` | Every third column, marching | yes |
| `Checkerboard` | Two drifting colors | yes |
| `SwirlIn`, `SwirlOut` | Rainbow spiral | yes |
| `BrickBreaker` | Breakout that plays itself | yes (bricks) |
| `Snake` | Snake that plays itself | yes |
| `PingPong` | Pong that plays itself | **no** |
| `Matrix` | Green falling trails | **no** |
| `LookingEyes` | Two eyes that look and blink | **no** |

For a calm background use `PlasmaCloud`, `Pacifica`, or `ColorWaves`. The game effects draw attention, so keep them for playful content.

## Weather overlays (`overlay`)

Drawn last, over everything. Text stays readable underneath.

| Overlay | Look | Speed |
|---|---|---|
| `drizzle` | Fine light-blue drops | ~10 steps/s |
| `rain` | Blue drops with short tails | ~15 |
| `storm` | Dense slanted streaks | ~25 |
| `thunder` | `storm` plus lightning every few seconds | ~25 |
| `snow` | Swaying gray flakes | ~7 |
| `frost` | Shimmering icy edge top and bottom; middle clear | ~10 |

A palette recolors all six. Per app, an overlay follows that app's `effectSpeed` and `palette`, and wins over the global one. Global: `<P>/cmd/display` with `{"overlay":"rain","overlaySettings":{"speed":0.3,"palette":"Ocean","blend":true}}`, and `null` to clear. Built-in apps show only the global overlay.

## Palettes (`palette`)

Each is 16 colors. Built in:

| Name | Colors |
|---|---|
| `Cloud` | Blues to sky blue and one white |
| `Lava` | Black, maroon, red, orange, one white peak |
| `Ocean` | Midnight blue, teal, aqua, light sky blue |
| `Forest` | Dark green to lime |
| `Stripe` | Eight strong colors alternating with black |
| `Party` | Purples, magentas, reds, oranges, yellows |
| `Heat` | Black, red, yellow, white |
| `Rainbow` | All hues |

Custom: a payload list of 1 to 16 colors, or `{"color","pos"}` stops at 0-100 (all or none). Stored: `/PALETTES/<name>.txt`, one `RRGGBB` or `RRGGBB@70` per line, made in the web UI's palette editor. A stored palette named like a built-in replaces it until the file is deleted. Stored palettes are not listed in capabilities.

To paint from a palette, set `textColor`, `chartColor`, or `progressColor` to `"palette"`. A palette belongs to its app only.

## Transitions

One setting for the whole device, so a notice has no transition of its own. Keys in `cmd/settings`: `transitionEffect` (default `Rain`), `transitionDirection` (`normal`, `reverse`), `transitionDurationMs` (default 1000).

Follow direction: `Slide`, `Rotate`, `Cover`, `Uncover`, `Wave`, `Rain`, `Melt`, `Interlace`.
Fixed direction: `Dim`, `Zoom`, `Pixelate`, `Curtain`, `Ripple`, `Blink`, `Reload`, `Fade`, `Split`, `Blinds`, `Blocks`, `Flash`, `Diamond`.
`Random` picks one of the other 21 each time.

`Flash` turns the display nearly white for a moment, so avoid it in a dark room.

## Colors

All color keys accept `"#FF00AA"`, `"FF00AA"`, `"F0A"`, `[255,0,170]`, `["HSV",320,100,100]` (`HSV` in capitals, s and v 0 to 100), or `16711850`. 8-digit hex is rejected: there is no transparency. The clock answers in uppercase `#RRGGBB`. For optional colors, `null` means inherit or off, not black.

## Whole-display color

Settings in `cmd/settings`, applied to every LED: `saturation` (100, `0` is gray), `gamma` (1.9), `colorCorrection` and `colorTint` (`null` is off; `#FFD6AA` warms). `colorTint` is an RGB color, not Kelvin. A screen capture does not include these.

## Fonts

| Font | Capital height | Rows | Note |
|---|---|---|---|
| `small` (default) | 5 px | 1-5 | Leaves rows for top drawings |
| `large` | 7 px | 0-6 | Leaves only the bottom row |
| `matrix-light6` | | 1-5 | Line height 6 |
| `matrix-chunky8x6` | | 0-6 | Line height 8 |

TC002 also has `matrix-chunky6`, `matrix-chunky6x`, `matrix-light6x`, `matrix-chunky8`, `matrix-chunky8x`, `matrix-light8`, `matrix-light8x`, `matrix-light8x6`. Character width is 4 px and a space is 2 px in `small` and `large`.

## Characters

Text is UTF-8. A missing character shows as one `?`.

Shown: ASCII, Latin-1 (`ä ö ü ß é`, also `° µ ·`), Latin Extended-A, Greek, Cyrillic, Vietnamese, IPA, `– —`, `€` and other currency signs, `℃ ℉`, and the Chinese and Korean date and weekday characters.

Shown as `?`: emoji, subscripts such as `₂`. In firmware 1.2.3 the `small` font's lookup table also has no `…` (U+2026), although the docs list it. Write `...` to be safe.

Width spaces: `⓪`, `①` to `⑩` are empty space of 0 to 10 px, useful for fine alignment.
