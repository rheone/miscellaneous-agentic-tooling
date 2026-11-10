---
name: homeassistant-awtrix-ng
description: >-
  Controls AWTRIX NG (Blueforcer firmware on Ulanzi TC001, TC002, or ESP32 pixel clocks) from
  Home Assistant over MQTT. Use when working with notifications, pushed apps and the app rotation, display look
  (icons, effects, overlays, palettes, fonts, charts, layouts), sounds, brightness and power, indicators,
  clock buttons and discovery entities, Berry scripts, a rejected AWTRIX payload, or porting an
  AWTRIX 3 automation. Not for AWTRIX 3 firmware: the two share no API.
license: PolyForm-Noncommercial-1.0.0
metadata:
  author: Robert Engelhardt <rheone@gmail.com>
  version: "2.1.0"
  firmware: "1.2.3"
  docs: https://blueforcer.github.io/awtrix-ng/
  upstream: https://github.com/Blueforcer/awtrix-ng
  credits: "AWTRIX NG firmware and documentation by Stephan Mühl (Blueforcer)"
---

# Home Assistant and AWTRIX NG

Home Assistant (HA) and the clock both talk to an MQTT broker. HA publishes JSON to `<P>/cmd/...`. The clock publishes state to `<P>/state/...`. `<P>` is the MQTT prefix: `mqttPrefix`, or the clock's 12-character MAC when that is empty. The clock's **MQTT prefix** sensor holds it.

Before you send a notification, search the HA config for a script that already publishes to `/cmd/notify`, and use it. It may apply Do Not Disturb or other gates that a direct publish skips.

## Choose the mechanism

| You want | Use | Lives until |
|---|---|---|
| A one-off message on top of everything | Notification: `<P>/cmd/notify` | It ends or is dismissed |
| A value that stays in the rotation | Pushed app: `<P>/cmd/apps/pushed/<name>` | Replaced, deleted, `lifetimeMs` ends, or the clock restarts. Re-push when `<P>/availability` turns `online` |
| Content that survives a reboot or has its own logic | Berry script on the clock | Deleted |
| A status dot at the right edge | Indicator: `<P>/cmd/indicators/1` to `3` | Changed |
| Weather over every app | Global overlay: `<P>/cmd/display` | Cleared |
| One color or white on the whole display | Mood light: `<P>/cmd/display/moodlight` | Turned off |
| Display on, off, brightness, volume, app stepping | The discovered HA entity | Saved or live |

## Publish JSON

```yaml
action: mqtt.publish
data:
  topic: "<P>/cmd/apps/pushed/power"
  payload: >-
    {{ {"text": states('sensor.power') ~ "W", "icon": "bolt", "textColor": "#FF8800"} | to_json }}
```

Build every payload as a dict and end with `| to_json`, so quotes in a state stay valid JSON. Publish commands with `retain: false`, the default: a retained command runs again at each reconnect. Keys are camelCase. Durations are whole milliseconds and end in `Ms`.

## Silent failures

A bad command looks like nothing happened, because MQTT returns no error to the publisher.

- **Rejected.** One unknown key, bad color, or unknown name rejects the whole payload. A notification-only key (`name`, `hold`, `stack`, `wakeup`, `sound`) on a pushed app counts. The reason appears only on `<topic>/result` and `<P>/event/error`.
- **Dropped.** A misspelled topic gets no answer, and neither does a message over 8192 bytes, topic included.
- **Skipped.** A value of the wrong type keeps the default: `"durationMs":"5000"` does nothing. Send numbers and booleans unquoted, and pass `text` and `icon` through `| string`: `"text": 21` shows nothing and `"icon": 636` shows no icon.
- **Deleted.** An empty payload deletes a pushed app, a mood light, or an indicator. Test with a real payload.
- **Cut off.** Long text ends when its time ends. Add top-level `"repeat": 1` to keep it until it has been read.

**A new payload is verified** when `<P>/event/error` stays silent (recipe in [recipes.md](references/recipes.md)) and the content appears in the frame from `<P>/cmd/screen/get`.

## Reference files

Read the rows that match the task, and only those.

| Task | File |
|---|---|
| Set up discovery, what each entity really does, prefix lookup, HTTP from HA | [home-assistant.md](references/home-assistant.md) |
| Working automations: sender script, several clocks, status app, re-push, buttons, knob, overlay, alarm, error log, live screen | [recipes.md](references/recipes.md) |
| Every command and state topic, `/result`, retain, QoS, limits | [mqtt.md](references/mqtt.md) |
| Every payload key: text, scroll, icon, timing, charts, progress, draw, notification keys | [payload.md](references/payload.md) |
| Names and looks: effects, overlays, palettes, transitions, colors, fonts, characters | [visuals.md](references/visuals.md) |
| Boxes of text, icons, and charts on a 52x16 clock | [layouts.md](references/layouts.md) |
| Icon files, formats, sizes, upload, storage | [icons.md](references/icons.md) |
| Melodies, RTTTL, volume, radio, speech, songs, what the clock can play | [sound.md](references/sound.md) |
| Settings, system config, device state fields, finding a clock, brightness, power, battery, sensors, backup, resets, firmware, security | [device.md](references/device.md) |
| Which clock this is, and what TC001, ESP32-S3 and TC002 can each do | [hardware.md](references/hardware.md) |
| Berry scripts, script MQTT, mirroring, Art-Net, mood light, voice | [advanced.md](references/advanced.md) |
| Porting from AWTRIX 3, clearing its retained topics, or upgrading from NG 1.1 | [migration.md](references/migration.md) |
| Something does not work | [troubleshooting.md](references/troubleshooting.md) |

Facts match firmware 1.2.3. On a newer clock, check names against the retained `<P>/state/capabilities` topic.

Based on [AWTRIX NG](https://github.com/Blueforcer/awtrix-ng) by Stephan Mühl (Blueforcer). See [NOTICE.md](NOTICE.md).
