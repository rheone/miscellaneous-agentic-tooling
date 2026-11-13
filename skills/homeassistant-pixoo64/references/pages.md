# Page types and components (divoom_pixoo 1.24.0)

Read from `sensor.py`, `pages/*.py` and `pixoo64/_colors.py` at 1.24.0. "Template" means the integration renders the value with Home Assistant's template engine. In a `show_message` call, Home Assistant has already rendered every template in `data` before the integration sees it (see [Where templates are rendered](#where-templates-are-rendered)).

## Contents

- [Page types](#page-types)
- [Components](#components)
- [Colors](#colors)
- [Where templates are rendered](#where-templates-are-rendered)
- [Built-in pages in detail](#built-in-pages-in-detail)

## Page types

`page_type` is lower-cased before use, so `PV` and `pv` are the same.

| `page_type` | Fields | Drawn by |
|---|---|---|
| `components` (alias `custom`) | `components` (list, required), `variables` (map, pages_data only) | The integration, one frame |
| `clock` | `id` (template) | The device: `Channel/SetClockSelectId`. Face IDs come from the Divoom app. |
| `channel` | `id` (template), 0-2 | The device: `Channel/SetCustomPageIndex` (custom channel page 1-3) |
| `visualizer` | `id` (template) | The device: `Channel/SetEqPosition`. `visualiser` is **not** accepted in 1.24.0. |
| `gif` | `gif_url` (template) | The device downloads and plays the file itself (`Device/PlayTFGif`, file type 2). Use a 64 x 64 GIF at a URL the Pixoo can reach. Fails on the Pixoo 64 II (issue #168). |
| `pv` | `power`, `storage`, `discharge`, `powerhousetotal`, `vomNetz`, `time` | The integration (fixed layout) |
| `fuel` | `title`, `name1`-`name3`, `price1`-`price3`, `status`, colors | The integration (fixed layout) |
| `progress_bar` | `header`, `progress`, `footer`, options | The integration (fixed layout) |

In the integration's `pages_data` (the page rotation), every page also takes `enabled` (template; `true yes 1 on` = shown) and `duration` (template, whole seconds). Inside a `show_message` call, these two keys are ignored.

## Components

### `text`

| Field | Required | Default | Notes |
|---|---|---|---|
| `content` | yes | - | Template. `\n` starts a new line. Drawn in the case given. |
| `position` | yes | - | `[x, y]`. x is the alignment anchor, y the cap line. **Not** template-rendered by the integration. |
| `font` | no | `pico_8` | Case-insensitive. Unknown: warning in the log, `pico_8`. See [fonts](fonts.md). |
| `color` | no | white | Template. See [Colors](#colors). |
| `align` | no | `left` | `left`, `center`, `right`. Other values: left. |

No `size`, no wrapping, no background, no scrolling. A failed template draws the text `Template Error`.

### `image`

| Field | Required | Default | Notes |
|---|---|---|---|
| `image_path` / `image_url` / `image_data` | one | - | Template. The first one present wins, in this order. `image_data` is base64. `image_url` is fetched on every draw (9 s timeout). |
| `position` | yes | - | `[x, y]` of the top-left corner. Not template-rendered by the integration. |
| `width`, `height` | no | original size | Both set: exact resize (can stretch). One set: shrink to fit that side, keep the aspect ratio, **never enlarge**. Not templates. |
| `resample_mode` | no | `box` | `nearest` (= `pixel_art`), `bilinear`, `hamming`, `bicubic`, `lanczos` (= `antialias`). Use `nearest` for pixel art and icons. |

- Images larger than 64 px are shrunk to fit 64 x 64.
- Fully transparent pixels are skipped (the background shows through). Partly transparent pixels are drawn at full color.
- `align` has no effect on images.
- Do not keep your own images in `custom_components/divoom_pixoo/img/`: an update replaces that folder. Use `/config/www/...`.

### `rectangle`

| Field | Required | Default | Notes |
|---|---|---|---|
| `position` | yes | - | `[x, y]` top-left. Each value is a template. |
| `size` | yes | - | `[width, height]` in pixels. Each value is a template. |
| `color` | no | white | Template. |
| `filled` | no | **true** | Template. Write `filled: false` for an outline. A string such as `"false"` that does not render to a real false counts as true. |

Use rectangles for backgrounds, bars, separators, status dots, progress bars and missing symbols (a minus sign).

### `templatable`

| Field | Required | Notes |
|---|---|---|
| `template` | yes | A template that renders to a list of component mappings. They are inserted right after this component and drawn in order. |

Useful in `pages_data` to build a variable number of rows. In a `show_message` call, a script template that builds the whole `components` list does the same job more simply. To lint the result, render the template first (for example `ha_eval_template`) and pass the output to `pixoo.py render`.

## Colors

`color` and the color fields of the built-in pages accept:

- `[R, G, B]`, each 0-255 (values outside are clamped), or a template that renders to that list;
- a CSS4 color name in **lower case**: `white`, `gray`, `lightskyblue`, `darkslateblue` and the rest of the CSS4 list (`pixoo64/_colors.py`).

Anything else, including `Red`, `#ff0000` and `rgb(255,0,0)`, silently becomes the default color (white for text and rectangles). `render` reports it as an error.

## Where templates are rendered

| Where the page lives | Who renders templates | Effect |
|---|---|---|
| `data.page_data` of a `show_message` action in an automation or script | Home Assistant first, then the integration renders the result again | Every field can use templates and script variables, including text and image positions. `variables:` inside `page_data` do not work (they are undefined when Home Assistant renders). |
| `pages_data` in the integration's options (the rotation) | Only the integration, at each draw | Only the fields marked "template" above. `variables:` work. Text and image `position` must be plain numbers. |

A template whose whole output looks like a number or a list becomes that type. `content: "{{ x }}"` with `x = 11.10` shows `11.1`. Keep a unit in the same string.

## Built-in pages in detail

These pages use fixed positions and fonts, so long text overflows without warning.

### `progress_bar`

| Field | Default | Notes |
|---|---|---|
| `header` | - | `five_pix` at `(header_offset, 1)` on a gray bar. About 13 characters. |
| `progress` | - | Goes through `int()`: `45.5` becomes 45; `unavailable` or other text raises `ValueError` and the page is not drawn. Use `| int(0)`. |
| `footer` | - | `five_pix` at `(footer_offset, 58)`. |
| `time_end` | empty | Only digits and `:` are kept; drawn in `clock` font below the bar. |
| `bg_color` | `[0, 123, 255]` | |
| `header_font_color`, `footer_font_color`, `progress_text_color` | white | |
| `progress_bar_color` | `[255, 0, 68]` | |
| `time_color` | `[51, 51, 51]` | The current time (`clock` font). |
| `time_end_color` | `[151, 151, 151]` | |
| `header_offset`, `footer_offset` | 2 | x of the text. |

`five_pix` has no `/ ' + ( ) &`, so a header like "3D print (PLA)" loses characters.

### `fuel`

Title in `eleven_pix`, upper-cased by the page (about 9 characters). Names in `five_pix` (cut at x=31), prices in `gicko`, status in `five_pix`. Colors: `font_color` white, `bg_color` `[255, 230, 0]`, `price_color` white, `title_color` black, `stripe_color` white. `title_offset` 2.

### `pv`

Every field except `time` must render to a number (`float()`); `unavailable` stops the page. Use `| float(0)`. Numbers are drawn as floats (`1234.0`). Icons come from the integration's `img/` folder. The layout is fixed and was made for German solar setups (`vomNetz` = from the grid).
