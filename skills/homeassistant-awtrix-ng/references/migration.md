# Porting from AWTRIX 3

Migrate by error: send the old payload to the new topic, read `field` on `<topic>/result`, rename that key, repeat until `{"ok":true}`. The upstream guide has a paste-in converter for HA automations and blueprints: `https://blueforcer.github.io/awtrix-ng/guides/migrating-from-awtrix3/`.

## Topics

| AWTRIX 3 | AWTRIX NG |
|---|---|
| `[prefix]/custom/x` | `<P>/cmd/apps/pushed/x` (empty still deletes) |
| `[prefix]/notify` | `<P>/cmd/notify` |
| `[prefix]/nextapp`, `previousapp`, `switch` | `<P>/cmd/apps/next`, `previous`, `switch` |
| HTTP `POST /api/custom?name=x` | `PUT /api/v1/apps/pushed/x` (delete with `DELETE /api/v1/apps/x`) |
| HTTP `POST /api/notify` | `POST /api/v1/notifications` |
| HA `awtrix.*` actions (custom integration) | `mqtt.publish` |

## Keys

| AWTRIX 3 | AWTRIX NG |
|---|---|
| `color` | `textColor` |
| `{"t":..,"c":..}` text pieces | `{"text":..,"color":..}` |
| `textCase` 0/1/2 | `"inherit"`/`"upper"`/`"asTyped"` |
| `center` true/false | `textAlign` `"center"`/`"start"` |
| `textOffset` | `textOffsetX` |
| `gradient: [a,b]` | `palette: [a,b]` + `textColor: "palette"` |
| `rainbow` | `palette: "Rainbow"` + `textColor: "palette"` |
| `blinkText`, `fadeText` | `textBlinkMs`, `textFadeMs` |
| `background` | `backgroundColor` |
| `noScroll` | `scroll: {"mode":"static"}` |
| `scrollSpeed` | `scroll: {"speed":N}` |
| `pushIcon` 0/1/2 | `iconMode` `"fixed"`/`"pushOnce"`/`"push"` |
| `duration` seconds | `durationMs` (x1000) |
| `lifetime` seconds | `lifetimeMs` (x1000) |
| `lifetimeMode` 0/1 | `lifetimeExpiry` `"remove"`/`"mark"` |
| `repeat: -1` | `repeat: 0` |
| `bar`, `line`, `autoscale` | `barChart`, `lineChart`, `chartAutoscale` |
| `progressC`, `progressBC` | `progressColor`, `progressTrackColor` |
| `effectSettings.speed` | `effectSpeed` (0.1 to 10 multiplier) |
| `effectSettings.palette`, `.blend` | `palette`, `paletteBlend` (top level) |
| `rtttl` | `sound: {"rtttl":"..."}` |
| `loopSound` | `"loop": true` inside `sound` |
| `overlay: "clear"` | `overlay: ""` |
| `MATP` setting | `<P>/cmd/display` with `{"power":false}` |

## Draw commands

Objects became arrays with a spelled name: `dp` pixel, `dl` line, `dr` rect, `df` rectFill, `dc` circle, `dfc` circleFill, `dt` text, `db` bitmap.

`{"dp":[28,4,"#F00"]}` becomes `["pixel",28,4,"#F00"]`.

## No equivalent

- `topText`: use a `draw` text command.
- `barBC`: unfilled chart cells show the background.
- `clients`: have the automation send to each clock.
- `pos`: set the whole rotation once with `<P>/cmd/apps/order`, which is saved across reboots.
- `save`: pushed apps are not kept. Re-push after a restart, or write a script.
- MQTT placeholder `.json` files: a script can subscribe.

## Also different

- Effect names differ. Check them against [visuals.md](visuals.md).
- Icons with the same IDs still work, but a fresh install starts with none.
- Device settings do not import. Battery calibration works differently.
- Inline base64 icons need the `data:image/...;base64,` prefix.

## Clear old retained topics

AWTRIX 3 published retained discovery and state topics, and they stay on the broker after the firmware changes. Deleting its entities from the HA registry is not enough: they return, with live-looking old values, at the next HA restart.

1. List what is retained. `<uid>` is the MAC without separators, and `<old-prefix>` is the AWTRIX 3 MQTT prefix:

    ```bash
    mosquitto_sub -h <broker> -u <user> -P <pass> -v --retained-only -W 3 \
      -t 'homeassistant/+/<uid>/#' -t '<old-prefix>/#'
    ```

2. Publish an empty retained message to each old topic, usually `homeassistant/<type>/<uid>/<unique_id>/config` and `<old-prefix>/<uid>/<unique_id>/stat_t`:

    ```bash
    mosquitto_pub -h <broker> -u <user> -P <pass> -r -n -t '<topic>'
    ```

    From HA, use `mqtt.publish` with `payload: ""` and `retain: true`.

3. Leave `homeassistant/device/<uid>/config` alone. That one is AWTRIX NG's own discovery message.

HA removes the old entities by itself once their discovery topics are empty.

## Checklist

1. Rewrite the topic, and every key in the tables above.
2. Remove `save` and add a re-push on `<P>/availability`.
3. The port is done when every payload the automation can send has answered `{"ok":true}`, including its templated branches.

## Upgrading from NG 1.1 to 1.2

Automations written for NG 1.1.x need these changes. The old keys are refused with `422`.

| 1.1 | 1.2 |
|---|---|
| `"soundRtttl":"..."` | `"sound":{"rtttl":"..."}` |
| `"soundLoop":true` | `"loop":true` inside `sound` |
| `"sound":3` | `"sound":{"track":3}` |
| `{"mp3":"x"}`, `{"melody":"x"}` on `audio/play` | `{"file":"x"}` or `"x"` |
| `{"scope":"sounds"}`, `{"scope":"stream"}`, `{"scope":"all"}` on `audio/stop` | `{"group":"alert"}`, `{"group":"radio"}`, `{}` |
| `mp3Volume`, `buzzerVolume`, `dfplayerVolume`, `soundEnabled` | `volume`, `appVolume`, `alertVolume` (`volume: 0` mutes) |
| `icon` as plain base64 | A `data:image/...;base64,` URL |

Also changed: volumes reset to defaults, so a muted clock makes sound again until you set `volume`. Button topics are no longer retained. An indicator command without `blinkMs` or `fadeMs` gives a steady light. Error message text changed, so compare `code`, not the message.
