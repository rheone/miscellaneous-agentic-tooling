# Notification and pushed-app payload

One format serves both. Any key not listed here or in [layouts.md](layouts.md) is an error. For effect, palette, and font names see [visuals.md](visuals.md).

## Text

| Key | Type and values | Default | Meaning |
|---|---|---|---|
| `text` | String, or `[{"text":"CPU ","color":"#888"},...]` | `""` | A number or boolean here is ignored |
| `textCase` | `inherit`, `upper`, `asTyped` | `inherit` | Global `uppercase` is on, so text shows in capitals |
| `font` | `small`, `large`, `matrix-light6`, `matrix-chunky8x6` (TC002 has more) | `small` | Use `small` if something draws in the top row |
| `textColor` | Color or `"palette"` | Global `#FFFFFF` | Ignored with pieces, unless `"palette"` |
| `textBlinkMs`, `textFadeMs` | ms, 0 off | 0 | Period |
| `textAlign` | `start`, `center`, `end` | `center` | Still text only |
| `textOffsetX` | px | 0 | Left or right only |
| `textInFront` | bool | `false` | Text over charts and drawings |
| `scroll` | Object, or a mode string | Global | See below |
| `repeat` | int | 0 | Top level, beside `text`. See Timing |

Color priority for plain text: palette, then fade, then blink, then `textColor`.

### `scroll`

| Field | Values | Default |
|---|---|---|
| `mode` | `static` (cut off), `wrap`, `loop` (ticker), `bounce` | `wrap` |
| `direction` | `left`, `right` | `left` |
| `entry` | `inline`, `offscreen` | `inline` |
| `whenFits` | `static`, `scroll` | `static` |
| `speed` | Percent of 21 px/s. Stays sharp to about 200 | 100 |
| `gap` | px between `loop` repeats | 8 |
| `holdMs` | Pause at start and at `bounce` ends | 1000 |

Omitted fields follow the global `scroll` setting.

## Timing

| Key | Default | Meaning |
|---|---|---|
| `durationMs` | 0 (global 7000) | Time shown. Ignored with `hold` |
| `repeat` | 0 | Scroll runs before it ends. Has no effect when text is still. With `durationMs`, it stays at least that long |
| `lifetimeMs` | 0 (forever) | Pushed app only. Counts from receipt |
| `lifetimeExpiry` | `remove` | Or `mark`: stays, with a dark-red frame |

## Icon

| Key | Default | Meaning |
|---|---|---|
| `icon` | `""` | File ID (up to 64 characters), or a `data:image/gif;base64,...` or `data:image/jpeg;base64,...` URL. TC002 also takes a web address |
| `iconMode` | `fixed` | `pushOnce` or `push`: scrolling text pushes it off |
| `iconOffsetX` | 0 | Left or right, can cover text |
| `iconGap` | 1 | 0 to 128 empty columns |
| `icons` | `[]` | Up to 4 of `{"icon","x","y"}`, freely placed, taking no text space |

A missing icon is left out, and the text centers as if none was set. A GIF as wide as the display becomes the background and replaces the effect. See [icons.md](icons.md).

## Background, effect, overlay

| Key | Default | Meaning |
|---|---|---|
| `backgroundColor` | Black | Ignored when `effect` is set |
| `effect` | `""` | Unknown name: rejected |
| `effectSpeed` | 1.0 | 0.1 to 10, clamped. Also sets the app's overlay speed |
| `overlay` | `""` | `rain`, `snow`, `drizzle`, `storm`, `thunder`, `frost`. Wins over the global overlay |
| `palette` | None | Name, up to 16 colors, or stops `{"color","pos"}`. Shared by text, charts, progress, effect, overlay |
| `paletteBlend` | `true` | `false` gives 16 hard bands |
| `paletteSpan` | 0 | Pixels per palette run on text. 0 stretches once |
| `paletteSpeed` | 0 | Palette runs per second on text |

## Charts and progress

| Key | Default | Meaning |
|---|---|---|
| `barChart`, `lineChart` | `[]` | Up to 16 whole numbers. A line needs 2 |
| `chartAutoscale` | `true` | `false` fixes the range at 0 to 8 |
| `chartColor` | Text color | Or `"palette"`: colors by value |
| `progress` | -1 | 0 to 100, bottom row. Below 0 is off. 0 draws the full track |
| `progressColor` | `#00FF00` | Or `"palette"` |
| `progressTrackColor` | `#FFFFFF` | Plain color only |

Charts start after the icon at `x=9`. Progress starts at the icon's edge at `x=8`. The bar always draws its track, so give it the background color to hide it.

## Draw commands

`"draw"` is a list of arrays, drawn in order. Positions count from the left edge, ignoring any icon. Outside the display is clipped silently.

| Command | Arguments |
|---|---|
| `["pixel", x, y, color]` | One pixel |
| `["pixels", color, x1, y1, x2, y2, ...]` | Many pixels |
| `["line", x1, y1, x2, y2, color]` | Both ends included |
| `["rect", x, y, w, h, color]` | Outline. `w` and `h` are a size, not a corner |
| `["rectFill", x, y, w, h, color]` | Filled |
| `["circle", cx, cy, r, color]`, `["circleFill", ...]` | Center and radius |
| `["text", x, y, "HI", color]` | Still, cut off, unstyled. `y=1` matches the app's own text rows |
| `["bitmap", x, y, w, h, data]` | Base64 RGB888, or a list of colors |

A trailing color may be omitted to use the text color. One bad command rejects the request, with `field` like `draw[2]`.

## Notification-only keys

| Key | Default | Meaning |
|---|---|---|
| `name` | `""` | For dismissing this one. URL-safe. `active` is reserved |
| `hold` | `false` | Stays until dismissed. Blocks the queue behind it |
| `stack` | `true` | `false` replaces the one shown; the queue stays |
| `wakeup` | `false` | Shows while the display is off. Without it, nothing shows |
| `sound` | None | See [sound.md](sound.md) |

## Draw order

1. Effect, or background color, or black.
2. Text and drawings. Drawings order: `draw`, progress, bar chart, line chart. Text is under them unless `textInFront`.
3. The expired `mark` frame.
4. Icon, then `icons`.
5. Overlay, last.

## What is refused

The whole payload is rejected for invalid JSON, an unknown key, an unreadable color, a word outside its list, an unknown effect, overlay, or palette, a sound with a mistake, or a wrong draw command. A value of the wrong type on a number, boolean, `text`, `icon`, `effect`, `overlay`, or `name` key is ignored and the key keeps its default. `iconGap` is the exception: a wrong type there is refused. A pushed-app array `[{...},{...}]` makes numbered apps `name0`, `name1`, and is all or nothing.
