# Clock hardware

There is one firmware per chip, not per board. Find what you have from `<P>/state/device` (`boardType`, `soc`) and `<P>/state/capabilities`, or `GET /api/v1/capabilities`.

| | Ulanzi TC001 / ESP32 | ESP32-S3 build | Ulanzi TC002 |
|---|---|---|---|
| `soc` | `esp32` | `esp32s3` | `armv7l` |
| Display | 32x8 (DIY up to 128x8) | 32x8 (DIY up to 128x8) | 52x16, fixed |
| Input | 3 buttons | 3 buttons | 3 buttons, knob |
| Sound | Buzzer (RTTTL). DFPlayer optional | Adds MP3, songs, radio with I2S and PSRAM | Speaker: MP3, songs, speech, radio |
| Microphone | No | No | Yes |
| Light sensor | Yes on TC001 | If wired | No |
| Temp and humidity | Yes on TC001 | If wired | No |
| Battery | Yes on TC001 | If wired | Yes, reports charging |
| Built-in apps | Time, Date, Temperature, Humidity, Battery | Same | Time (five faces), Status |
| Max HTTP body | 8192 bytes | 8192 bytes | 2 MiB |
| Max MQTT message | 8192 bytes | 8192 bytes | 8192 bytes |
| MQTT TLS | No | No | Yes |
| Deep sleep | Yes | Yes | No |
| File storage | 512 KB on 4 MB flash | Up to 12.5 MB on 16 MB | Larger; 1 MiB held free |
| Layouts, web icons, voice | No | No | Yes |

## Display layout

`x` counts columns from 0 at the left, and `y` counts rows from 0 at the top. The right edge holds the three indicators: 1 top, 2 middle, 3 bottom. The left edge shows connection problems, which cannot be turned off:

| Dot | Meaning |
|---|---|
| Red, top-left, pulsing | Not on Wi-Fi |
| Yellow, bottom-left, pulsing | No MQTT broker connection |

## TC002 differences for payloads

Pushed apps and notifications draw at double size on a 26x8 grid (`enlargeApps`, on by default), so about 6 characters fit. `draw` positions count on that grid: the bottom-right is `["pixel",25,7]`. An icon bigger than 26x8 keeps full size. Scripts and layouts use all 52x16 pixels. A payload written for 32x8 can place drawings off the 26-column grid.
