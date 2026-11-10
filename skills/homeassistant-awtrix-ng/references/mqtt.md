# MQTT topics

Command payloads are the same JSON as the HTTP bodies. To convert an HTTP route, put `cmd/` in front of the path after `/api/v1/`; notifications are `cmd/notify` and switching is `cmd/apps/switch`.

## Commands

| Topic | Payload | Notes |
|---|---|---|
| `<P>/cmd/notify` | Notification JSON | See [payload.md](payload.md) |
| `<P>/cmd/notify/dismiss` | Ignored | Dismisses the one shown |
| `<P>/cmd/notify/dismiss/<name>` | Ignored | Any position in the queue. Unknown name: `notFound` |
| `<P>/cmd/apps/pushed/<name>` | Pushed-app JSON. **Empty or `{}` deletes** | Name: `[A-Za-z0-9_-]{1,32}`. Reserved: `active`, `next`, `previous`, `order` |
| `<P>/cmd/apps/switch` | App name, or `{"name":"Time","fast":true}` | An app that is off answers `notFound` |
| `<P>/cmd/apps/next`, `/previous` | Ignored | |
| `<P>/cmd/apps/order` | `{"order":[...],"disabled":[...]}` | `disabled` required and complete. `order` optional. A name may repeat for more screen time |
| `<P>/cmd/apps/<name>/enabled` | `true` or `false` | One app only |
| `<P>/cmd/settings` | Partial settings JSON | See [device.md](device.md) |
| `<P>/cmd/settings/reset` | Ignored | **Deletes settings and restarts** |
| `<P>/cmd/display` | `{"power":bool,"overlay":"rain"\|null,"overlaySettings":{...}}` | All keys optional |
| `<P>/cmd/display/moodlight` | `{"color"\|"kelvin","brightness"}`. **Empty turns off** | `kelvin` wins over `color`. Brightness is not range checked: 300 wraps to 44 |
| `<P>/cmd/indicators/1` to `/3` | `{"color","blinkMs","fadeMs"}`. **Empty or `{}` turns off** | Other IDs are ignored without an answer |
| `<P>/cmd/audio/play` | A sound: see [sound.md](sound.md) | 1 to 4 entries as a list |
| `<P>/cmd/audio/stop` | Empty or `{"group":"alert"\|"app"\|"radio"}` | |
| `<P>/cmd/audio/stations` | `{"stations":[...]}` | Radio clocks only |
| `<P>/cmd/device/reboot` | Ignored | **Loses pushed apps.** `/result` may not arrive |
| `<P>/cmd/device/sleep` | `{"durationMs":60000}` | **Unreachable until it wakes.** ESP32 only; on TC002 it only restarts AWTRIX |
| `<P>/cmd/screen/get` | Ignored | Reply on `state/screen` |
| `<P>/cmd/voice/start` | Ignored | TC002 only |

**HTTP only:** system configuration (`/api/v1/system`, including MQTT and time zone), file uploads, the app list, installing or deleting scripts, storing melodies, factory reset. Publishing to `cmd/device/factory-reset` does nothing.

## Replies

Every recognized command answers on `<topic>/result`, not retained:

```json
{"ok":true}
{"ok":false,"error":{"code":"validationFailed","message":"out of range","field":"brightness"}}
```

Codes over MQTT: `invalidJson`, `validationFailed`, `notFound`, `insufficientStorage`, `unavailable`, `internalError`, `invalidName`, and `serviceBusy` (ESP32-S3 radio).

A topic the clock does not know gets no reply. Neither does a message over 8192 bytes, counting the topic. Messages over 64 KiB also make the clock reconnect to the broker.

`<P>/event/error` reports every rejected command from MQTT or HTTP, with `source`, `request`, and `error`. Subscribe to it instead of many `/result` topics.

## State

| Topic | Content | Retained | When |
|---|---|---|---|
| `<P>/availability` | `online` or `offline` | yes | Connect; last will |
| `<P>/state/device` | The `GET /api/v1/device` object | yes | Every `statsInterval`, and within 250 ms of a power or indicator change |
| `<P>/state/settings` | All settings | yes | On change and connect |
| `<P>/state/apps/active` | App name, plain text | yes | On change |
| `<P>/state/audio` | What is playing | yes | On change |
| `<P>/state/capabilities` | Valid names and hardware | yes | Once per connect |
| `<P>/state/prefix` | The prefix, plain text | yes | Once per connect |
| `<P>/state/buttons/left`, `/select`, `/right` | `1` or `0` | no | Each press and release, and on connect |
| `<P>/state/buttons/knob`, `<P>/event/knob` | `1`/`0`; `{"turn":N}` | no | TC002 |
| `<P>/event/error` | Rejected command | no | When it happens |
| `<P>/state/screen` | Pixels | no | Reply to `cmd/screen/get` |

Payloads on `state/capabilities` include `effects`, `paletteEffects`, `transitions`, `overlays`, `palettes`, `audio`, and `sensors`. Publishing to a state topic does nothing.

## Delivery

QoS 0 everywhere, so a lost message is not sent again. After a failed connection the clock retries after 5, 10, 20, and 40 seconds, then every 60. Neither MQTT nor HTTP limits how often you send.

## Limits

| Thing | Limit | Past it |
|---|---|---|
| Pushed apps | 50 | `insufficientStorage`. Replacing an existing one always works |
| Notification queue | 32 with the one shown | `insufficientStorage`. `stack:false` always works |
| Notifications per message | 1 | `validationFailed` |
| Chart points | 16 | Extras dropped |
| Extra `icons` | 4 | `validationFailed` |
| JSON nesting | 16 levels | `invalidJson` |
| RTTTL | 512 characters | `validationFailed` |

Keep draw payloads short: use `#F00` colors, omit repeated colors, group with `pixels`, and use base64 for bitmaps.
