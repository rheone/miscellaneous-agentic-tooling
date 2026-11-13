# Connecting Home Assistant

## Set up discovery

Needs HA 2024.11 or newer and the MQTT integration. In the clock's web UI: **System > MQTT**, turn on **Enable MQTT**, set the broker, turn on **HA discovery**, save, and reboot. Broker settings are read once at start-up. Discovery can change at any time.

Over HTTP:

```bash
curl -X PUT http://<ip>/api/v1/system -H "Content-Type: application/json" \
  -d '{"mqttEnabled":true,"mqttHost":"192.168.1.10","mqttPort":1883,"mqttUser":"awtrix","mqttPass":"secret","mqttPrefix":"awtrixNG","haDiscovery":true}'
curl -X POST http://<ip>/api/v1/device/reboot
```

With `mqttPrefix` empty, the prefix is the clock's 12-character MAC. Give each clock its own prefix: clocks that share one all act on every command. Changing a prefix means changing every automation that names it, so look it up from the sensor (below).

Discovery is one retained message on `<haPrefix>/device/<uid>/config`. Turning `haDiscovery` off publishes an empty retained message there, which removes the device from HA. The command topics keep working either way.

## Entities

| Entity | Type | Does | Notes |
|---|---|---|---|
| Matrix | `light` | Power, brightness (0-255), RGB | **RGB sets the default text color, not a tint.** Keep it out of scenes unless you mean that |
| Indicator 1, 2, 3 | `light` | RGB dots on the right edge | Toggle on gives white. Using the entity stops blink and fade |
| Brightness mode | `select` | `Manual` or `Auto` | Needs a light sensor. Set `Manual` before you expect the slider to work |
| Transition effect | `select` | The 22 transition names | Whole device |
| Transition | `switch` | `autoTransition` | Off stops the rotation |
| Next app, Previous app | `button` | Step the rotation | |
| Dismiss notification | `button` | Clears the notice shown | The next one in the queue shows at once |
| Stop sound | `button` | Stops all sound | Sound hardware only |
| Volume, App volume, Alert volume | `number` | 0-100, step 5 | Radio volume too on clocks with radio |
| Current app, Version, IP address, MQTT prefix, WiFi strength, Uptime, Free RAM | `sensor` | Read-only | Most are diagnostic |
| Light level | `sensor` | 0-100 percent | Relative, not lux |
| Temperature, Humidity, Pressure | `sensor` | As the sensor measures | Absent without that sensor |
| Battery, Battery voltage | `sensor` | Estimate from voltage | Absent without a battery pin |
| Low battery | `binary_sensor` | Below `lowBatteryThreshold` | Stays off until the threshold is above 0 |
| Button left, select, right | `binary_sensor` | `on` while held | Not retained. `unknown` after an HA restart until a press or reconnect |
| Assist, Charging, Knob, Knob turn | TC002 only | See [advanced.md](advanced.md) | |

An entity exists only if the hardware does. Base count is 19. There is no notification entity.

Update timing: power and indicators publish within 250 ms. Settings and the current app publish on change. Everything else in `state/device`, brightness included, waits for `statsInterval` (default 10 s).

With auto-brightness on, the slider follows the room and a value you set has no effect.

## The clock in light sweeps

The Matrix and the three indicators are `light` entities. Anything aimed at lights in general also darkens the clock: `light.turn_off` on an area, an "all lights off" script, a label sweep, or a voice command. A dark clock also hides notifications that lack `wakeup`, so the cause can look like a broken automation.

If the clock is a display and not a lamp:

- Give the clock's lights a label such as `display`, and exclude it in sweeps: `| reject('in', label_entities('display'))`.
- Hide those four entities, so auto-generated dashboards skip them. Explicit cards still work.
- Remove them from voice exposure.
- If you assign the clock to an area, remember that `area_id` targets include its lights.

## Find the prefix from a device

Use this in a blueprint or a shared script, where the user picks the clock:

```jinja
{% set e = device_entities(device_id) | select('search', 'mqtt_prefix') | list %}
{{ states(e[0]) if e else 'unknown' }}
```

Filter the device selector with `integration: mqtt` and `manufacturer: Blueforcer`. Stop if the result is `unknown` or `unavailable`. The match is on the entity ID, so a rename breaks it.

## Read extra device state

`<P>/state/device` is retained JSON with more than the entities show; [device.md](device.md) lists the fields. Hardware-dependent keys are left out, not null, so use `value_json.key | default(...)`. Make a trigger-based template sensor on the topic when you need one.

Base logic on state topics, not on the command you sent. QoS is 0 everywhere, so a command can be lost.

## Availability

`<P>/availability` is `online` or `offline`, retained, and the broker publishes `offline` as the last will. Entities go unavailable by themselves.

## HTTP from Home Assistant

Prefer MQTT. Use `rest_command` only for what has no MQTT form: `PUT /api/v1/system`, uploads, deleting scripts, factory reset.

```yaml
rest_command:
  awtrix_system:
    url: "http://<ip>/api/v1/system"
    method: PUT
    content_type: "application/json"
    username: !secret awtrix_web_user
    password: !secret awtrix_web_password
    payload: "{{ body | to_json }}"
```

`content_type` is required: a `PUT` or `PATCH` with a form type gets `415`. The login covers the whole HTTP API and web UI, not MQTT.

## Ready-made flows

The AWTRIX Hub (`https://awtrix.de`) has HA blueprints with an **Import to Home Assistant** button. These are community content, so read a blueprint before you import it.
