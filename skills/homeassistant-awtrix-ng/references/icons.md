# Icons

A new install has no icons. Each is a GIF or JPEG in `/ICONS`, and its file name without the extension is its ID: `sun.gif` is `"icon":"sun"`. IDs are case-sensitive.

## Get icons on the clock

| Way | How |
|---|---|
| AWTRIX Hub | Web UI **Icons > Add > Icons for this device**, or `https://awtrix.de/icons`, then **Send to AWTRIX**. Downloads need a Hub sign-in. Hub icons are named, for example `sun` |
| Web UI upload | **Icons > Add**. Takes GIF, PNG, JPG and converts PNG and JPG to GIF |
| Icon editor | Draw or edit in the web UI, with a live preview on the display |
| API | `curl -X POST "http://<ip>/api/v1/files?dir=/ICONS" -F "file=@1234.gif"`; add `-u user:pass` when login is on |
| Inside the payload | `data:image/gif;base64,...` or `data:image/jpeg;base64,...`, within the 8192-byte limit |

The API refuses PNG with `415`, even renamed, because it reads the content. Convert first. LaMetric icons (`https://developer.lametric.com/content/apps/icon_thumbs/<id>`) sometimes arrive as PNG.

## Format and size

Prefer GIF: JPEG looks blurry at this size. The clock looks for `/ICONS/<id>.gif` first, then `.jpg`.

| Format | Size |
|---|---|
| JPEG | Always 8x8. Larger shows only the top-left 8x8 |
| GIF | Keeps its own size, up to the display size. Animated or still |
| GIF as wide as the display | Becomes the background and replaces the effect |

GIFs loop forever. A frame delay of 0 becomes 100 ms. Transparent pixels are black on the first frame and keep the previous frame afterward. An icon lower than the display is centered vertically.

## Layout

An 8-pixel icon takes 8 columns plus a 1-column gap, so text starts at column 9. Text moves only when it does not fit. Drawing commands ignore the icon, so a shape beside it starts at `x=9`.

`"iconMode":"push"` lets scrolling text push the icon off and back each run. `pushOnce` does it once. `icons` places up to 4 more images, each animating alone.

## Manage files

```bash
curl "http://<ip>/api/v1/files?dir=/ICONS"                        # list, usedBytes, totalBytes
curl -X DELETE "http://<ip>/api/v1/files?path=/ICONS/1234.jpg"    # full path
curl http://<ip>/ICONS/1234.jpg -o 1234.jpg                       # download
```

Storage is shared by icons, melodies, palettes, and scripts: 512 KB on a 4 MB board, 4.5 MB on 8 MB, 12.5 MB on 16 MB. A full store answers `507`. Use small, short GIFs.

## Good to know

- A factory reset or a fresh firmware install deletes all icons. A settings reset keeps them. Keep the icon set in a backup or a repeatable upload script.
- Without a web login, anyone on the network can upload and delete files.
- After a rename, every app that uses the old name shows no icon.
- If both `mail.gif` and `mail.jpg` exist, the GIF always wins.
- Only TC002 accepts `http(s)://` picture addresses as icons. See [advanced.md](advanced.md). On ESP32 a web address is accepted but shows nothing.
