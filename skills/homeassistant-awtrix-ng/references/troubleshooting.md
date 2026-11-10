# Troubleshooting

Start by reading what the clock answers, then match the symptom. From HA, use the error-log automation in [recipes.md](recipes.md). From a shell:

```bash
mosquitto_sub -h <broker> -t '<P>/event/error' -v
mosquitto_sub -h <broker> -t '<P>/cmd/#' -v
```

## A command does nothing

| Symptom | Cause | Fix |
|---|---|---|
| No `/result` at all | Topic misspelled or unknown | Compare with [mqtt.md](mqtt.md) |
| No `/result`, large payload | Over 8192 bytes with the topic | Shrink it. The clock's log names the drop |
| `validationFailed` with `field` | Unknown key, bad value, or wrong name | Fix that key and send again. Only the first problem is named |
| `invalidJson` | Template built JSON by hand | Build a dict and use `to_json` |
| `insufficientStorage` | 32 queued notices or 50 pushed apps | Send less often; delete apps; look for a `hold` blocking the queue |
| `{"ok":true}`, value unchanged | Wrong value type was skipped | Send numbers and booleans without quotes |
| A template produced an empty string | `states()` was unknown or unavailable | Guard with `not_to`, or a default |
| Blank text or no icon from a template | The value was a number, which those keys ignore | `| string` |

## Accepted, but nothing shows

Check in this order:

1. Display off: `matrixPower` in `<P>/state/device`. A notice needs `"wakeup": true`.
2. Mood light on: publish empty to `<P>/cmd/display/moodlight`.
3. Setup mode: the display shows `AP MODE`.
4. Art-Net stream running.
5. `hold` notice in front of it.
6. For a pushed app: its turn has not come, it is switched off, or the clock restarted and it is gone. Switch to it with `<P>/cmd/apps/switch`. `GET /api/v1/apps` shows `enabled`, `inLoop`, and `present`.

## Looks wrong

| Symptom | Cause | Fix |
|---|---|---|
| Text in capitals | `uppercase` is on | `"textCase":"asTyped"` |
| A `?` in the text | No such character | See Characters in [visuals.md](visuals.md) |
| Text cut off mid-scroll | The time ran out | Top-level `"repeat":1` |
| Text unreadable | Busy effect | `effectSpeed` 0.3, dark palette, or a calmer effect |
| No icon, text centered | ID does not match a file | Exact file name without extension, same case |
| Text under a chart | Default layer order | `"textInFront":true` |
| Background color ignored | An effect is set | Remove `effect` |
| Palette changes nothing | `PingPong`, `Matrix`, `LookingEyes` | Pick another effect |
| Built-in palette has odd colors | A file overrides it | Delete `/PALETTES/<name>.txt` |
| Different app after a notice | The rotation keeps turning behind a notice | Expected |
| Screen capture differs from LEDs | Capture excludes color settings | Check by eye |

## Home Assistant

| Symptom | Cause | Fix |
|---|---|---|
| No device | HA below 2024.11, discovery off, `haPrefix` wrong | Turn it on and match the prefix |
| Yellow dot, or `availability` empty | Broker unreachable | Read `mqtt` in `GET /api/v1/device` |
| Broker change has no effect | Read at start-up only | Reboot the clock |
| Broker logs `not authorised` after a password change | The new password needs a restart | Reboot the clock |
| Entities missing | Absent hardware | Expected; match against [hardware.md](hardware.md) |
| Dead entities return after an HA restart | Retained topics from old firmware | See Clear old retained topics in [migration.md](migration.md) |
| Clock goes dark with the room lights | The Matrix is a `light` entity | See The clock in light sweeps in [home-assistant.md](home-assistant.md) |
| Brightness slider has no effect | Auto-brightness | Set Brightness mode to `Manual` |
| Text color changed by a scene | Matrix RGB is `textColor` | Remove the Matrix light from the scene |
| Button sensors `unknown` | HA restarted | Clears at the next press or reconnect |

## MQTT connection errors

From `GET /api/v1/device`, object `mqtt`, field `error`:

| Error | Meaning |
|---|---|
| `hostNotFound` | Name did not resolve. Use an IP address instead of `.local` |
| `refused` | Nothing listening on that address and port |
| `badCredentials` | Wrong `mqttUser` or `mqttPass` |
| `rejected` | Broker refused. Check its log |
| `timeout` | Wrong port, usually |
| `lost` | Connection dropped. It reconnects by itself |

`connects` counting up with `lastError: lost` means repeated dropouts: a signal or router problem.

## Wrong time

- 00:00 on 1 January: NTP is blocked. Set `ntpServer` to a local server.
- Off by whole hours: `tz` is wrong. It is not validated. Pick the city again in the web UI.

## HTTP errors

| Code | Cause |
|---|---|
| `415` | `Content-Type` missing or a form type on `PUT` or `PATCH` |
| `400 invalidJson` on Windows | The shell removed the quotes. Send with `-d @file.json` |
| `422 body required` | Empty or `{}` on `PUT` of a pushed app or mood light. HTTP deletes use `DELETE` |
| `405` | `DELETE` on the `/pushed/` path; use `/api/v1/apps/<name>` |
| `401` | Web login is on. Add credentials |
| `200` on `/system`, no change | A reboot is needed, or the key was misspelled and discarded |

After a reboot, wait a few seconds before you check. Send the command only once.

## Further help

Logs: `GET /api/v1/logs` or the web UI **Log** tab. Docs: `https://blueforcer.github.io/awtrix-ng/`.
