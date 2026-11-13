# Layouts

A layout splits the display into boxes, each showing one thing. In firmware 1.2.3, only the TC002 supports it.

```json
{
  "durationMs": 10000,
  "layout": {
    "version": 1,
    "regions": [
      {"id": "title", "box": [0, 0, 52, 8], "text": "ENERGY", "font": "matrix-light6"},
      {"id": "load", "box": [0, 9, 40, 7], "chart": {"values": [20, 40, 30, 75], "type": "bar", "min": 0, "max": 100}},
      {"id": "battery", "box": [43, 9, 9, 7], "progress": 75, "color": "#00FF00"}
    ]
  }
}
```

Publish it to the normal notification or pushed-app topic. Nothing is stored on the clock.

## Rules

- A box is `[x, y, width, height]` on the full display. A layout does not use the double-size grid of ordinary apps. A layout that fills only the top-left quarter was counted on the wrong grid.
- Every box must lie inside the display, or the whole update is refused (`outside the display`).
- Regions draw in list order, and later ones cover earlier ones.
- Content is cut at the box edge. Fonts and images keep their size.
- A layout replaces `text`, `icon`, `draw`, `effect`, `scroll`, and the other drawing keys (`not allowed with layout`). Beside `layout` you can still use `durationMs`, `repeat`, `lifetimeMs`, `lifetimeExpiry`, and the notification-only keys.
- On a refused update, the previous content stays shown.

## Regions

Each region needs an `id`, a `box`, and exactly one content key.

| Content | Example | Options |
|---|---|---|
| `text` | `"text": "Hello"`, or `[{"text":"21.5","color":"#FA0"},{"text":"°C"}]` | `font`, `color`, `palette`, `align`, `valign`, `scroll`, `repeat`, `textCase`, `textBlinkMs`, `textFadeMs` |
| `icon` | `"icon": "sun"` | `align`, `valign`. A web address fills the whole region |
| `chart` | `"chart": {"values": [3,7,5]}` | `type` (`line`, `bar`), `min` and `max` (set both), `color`, `palette`. Up to 128 values |
| `progress` | `"progress": 75` | `color`, `palette`, `trackColor` (`#202020`) |
| `draw` | `"draw": [["circle",3,3,3,"#F00"]]` | `color`, `font`. Positions count from the box corner |

`align` and `valign` take `start`, `center`, or `end`. `align` applies only while text stands still. Set `color` or `textColor`, not both; `"palette"` paints from the region's or the layout's palette.

## Whole layout

Beside `version` and `regions`: `backgroundColor` or `effect` (not both), `effectSpeed`, `overlay`, `palette`, `paletteBlend`, `paletteSpan`, `paletteSpeed`.

## Updates

Regions match by `id`. Text that did not change keeps scrolling. A region whose text, font, box, or scroll changes starts again.

`repeat` beside `layout` keeps the app until every moving text has run that often. A region's own `repeat: 0` leaves that region out. A text with `speed: 0` never finishes.

## Limits

16 regions, 8 scrolling texts, 4 icons, 8192 bytes of text per layout. A text region counts as scrolling unless it sets `"scroll": "static"`. Over MQTT the whole message is still limited to 8192 bytes. All layouts share 256 KiB; when that is full, the request is refused. `layouts.limits` in capabilities has the numbers.
