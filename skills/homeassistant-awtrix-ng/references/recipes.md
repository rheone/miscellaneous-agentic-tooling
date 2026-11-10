# Recipes

Each block shows only the part specific to AWTRIX. Entity IDs are examples.

## One sender script for all notifications

A shared script gives every automation the same quiet-hours rule and keeps payload mistakes in one place. It drops empty fields because an empty color string is unreadable and rejects the whole notification.

```yaml
alias: Clock notify
mode: parallel
max: 10
fields:
  text: {required: true, selector: {text: {}}}
  icon: {selector: {text: {}}}
  color: {selector: {text: {}}}
  duration_s: {selector: {number: {min: 2, max: 120}}}
  urgent: {selector: {boolean: {}}}
  extra: {selector: {object: {}}}     # raw NG keys, merged last
sequence:
  - if:
      - condition: state
        entity_id: input_boolean.clock_quiet
        state: "on"
      - condition: template
        value_template: "{{ not (urgent | default(false)) }}"
    then:
      - stop: Quiet hours
  - action: mqtt.publish
    data:
      topic: "{{ states('sensor.clock_mqtt_prefix') }}/cmd/notify"
      payload: >-
        {% set d = {"text": text | string,
                    "durationMs": (duration_s | default(10) | float(10) * 1000) | int,
                    "icon": icon | default('') | string,
                    "textColor": color | default('')} %}
        {% set ns = namespace(o={}) %}
        {% for k, v in d.items() if v not in ['', none] %}
          {% set ns.o = ns.o | combine({k: v}) %}
        {% endfor %}
        {{ ns.o | combine(extra | default({})) | to_json }}
```

Script field `default:` values fill the UI only, so the template sets its own defaults. `mode: parallel` is right here: the clock queues notifications itself. Call it with `extra: {"overlay": "frost", "effectSpeed": 0.3}` for anything else.

## Send to several clocks

There is no broadcast key, so loop over the prefix sensors.

```yaml
repeat:
  for_each: >-
    {{ ['sensor.kitchen_clock_mqtt_prefix', 'sensor.office_clock_mqtt_prefix']
       | map('states') | reject('in', ['unknown', 'unavailable']) | list }}
  sequence:
    - action: mqtt.publish
      data:
        topic: "{{ repeat.item }}/cmd/notify"
        payload: '{"text":"Dinner"}'
```

## Keep a value in the rotation, and show when it goes stale

Push on change and on a timer. The `mark` expiry draws a thin dark-red frame if pushes stop, so an old number cannot pass as current.

```yaml
triggers:
  - trigger: state
    entity_id: sensor.power
    not_to: [unknown, unavailable]
  - trigger: time_pattern
    minutes: "/1"
  - trigger: mqtt            # the clock came back: pushed apps were lost
    topic: "<P>/availability"
    payload: "online"
actions:
  - action: mqtt.publish
    data:
      topic: "<P>/cmd/apps/pushed/power"
      payload: >-
        {{ {"text": states('sensor.power') ~ "W", "icon": "bolt",
            "lifetimeMs": 180000, "lifetimeExpiry": "mark"} | to_json }}
```

An unchanged text does not restart scrolling, and an unchanged icon keeps playing, so frequent pushes are safe. The retained `online` message also fires the MQTT trigger when HA restarts, which is harmless here. Set the rotation order once. It survives restarts, and a pushed app returns to its slot.

```yaml
action: mqtt.publish
data:
  topic: "<P>/cmd/apps/order"
  payload: '{"order":["Time","power","Date"],"disabled":["Battery"]}'
```

`disabled` is the complete off list, so every app it omits turns on. To switch one app, publish `true` or `false` to `<P>/cmd/apps/<name>/enabled`.

## Remove an app when it no longer applies

```yaml
action: mqtt.publish
data:
  topic: "<P>/cmd/apps/pushed/laundry"
  payload: "{}"
```

## An alarm that holds until dismissed

Name it so that the clearing automation removes only this one.

```yaml
action: mqtt.publish
data:
  topic: "<P>/cmd/notify"
  payload: >-
    {{ {"name": "leak", "text": "WATER LEAK", "textColor": "#FF0000", "textBlinkMs": 600,
        "hold": true, "stack": false, "wakeup": true,
        "sound": {"rtttl": "siren:d=8,o=5,b=200:c,g,c,g", "loop": true}} | to_json }}
```

Clear it by publishing anything to `<P>/cmd/notify/dismiss/leak`. A name not in the queue answers `notFound`, which is harmless. `hold` blocks every notice behind it, so keep held notices for real alarms.

## Progress for a running job

Update one app and let the update replace it.

```yaml
payload: >-
  {{ {"text": states('sensor.print_progress') ~ "%", "icon": "printer",
      "progress": states('sensor.print_progress') | int(0),
      "progressColor": "#00AAFF", "progressTrackColor": "#202020",
      "lifetimeMs": 600000} | to_json }}
```

## A chart from a forecast

```yaml
- action: weather.get_forecasts
  target:
    entity_id: weather.home
  data:
    type: hourly
  response_variable: fc
- action: mqtt.publish
  data:
    topic: "<P>/cmd/apps/pushed/forecast"
    payload: >-
      {% set t = fc['weather.home'].forecast[:16] | map(attribute='temperature')
         | map('round') | map('int') | list %}
      {{ {"lineChart": t, "chartColor": "#FF8800", "icon": "sun",
          "lifetimeMs": 7200000, "lifetimeExpiry": "mark"} | to_json }}
```

Charts take at most 16 whole numbers. A line chart needs at least 2.

## Weather over every app

Built-in apps show only the global overlay. Clear it with `null`.

```yaml
triggers:
  - trigger: state
    entity_id: weather.home
    not_to: [unknown, unavailable]   # any key here skips attribute-only updates
actions:
  - action: mqtt.publish
    data:
      topic: "<P>/cmd/display"
      payload: >-
        {% set m = {"rainy":"rain","pouring":"storm","snowy":"snow","snowy-rainy":"snow",
                    "lightning":"thunder","lightning-rainy":"thunder","hail":"storm"} %}
        {{ {"overlay": m.get(trigger.to_state.state)} | to_json }}
```

## Night mode

```yaml
action: mqtt.publish
data:
  topic: "<P>/cmd/settings"
  payload: '{"autoBrightness":false,"brightness":8,"volume":0}'
```

To darken the display entirely, turn off the Matrix light or publish `{"power":false}` to `<P>/cmd/display`. A notice shows through only with `"wakeup": true`, and MQTT, buttons, and apps keep running. A quick double press of select also toggles the display.

## A status light

```yaml
action: mqtt.publish
data:
  topic: "<P>/cmd/indicators/1"
  payload: '{"color":"#FF0000","blinkMs":500}'
```

An empty payload or `{}` turns it off. Every other payload resets blink and fade, so send them each time.

## Clock buttons as switches

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.clock_button_left
    from: "off"
    to: "on"
```

`from: "off"` skips the `unknown` to `on` change after a reconnect. The button still steps the rotation. Set `{"blockNavigation":true}` on `<P>/cmd/settings` if it should only drive your automation; one press of select still dismisses a notice. For a long press, add `for:` to the `on` state.

## Knob

On clocks with a knob, the Knob turn event has the types `clockwise` and `counterclockwise`, with the click count in its `steps` attribute.

```yaml
triggers:
  - trigger: event.received
    target:
      entity_id: event.clock_knob_turn
    options:
      event_type:
        - clockwise
actions:
  - action: light.turn_on
    target:
      entity_id: light.desk_lamp
    data:
      brightness_step_pct: "{{ 2 * (state_attr('event.clock_knob_turn', 'steps') | int(1)) }}"
```

Use `mode: queued` so fast turns are not lost. The knob still sets brightness and volume unless `blockNavigation` is on. Before HA 2026.7, use a `state` trigger on the event entity and read `event_type` from its attributes.

## Log every rejected command

```yaml
triggers:
  - trigger: mqtt
    topic: "<P>/event/error"
actions:
  - action: persistent_notification.create
    data:
      title: AWTRIX rejected a command
      message: >-
        {{ trigger.payload_json.request }}:
        {{ trigger.payload_json.error.code }}
        {{ trigger.payload_json.error.field | default('') }}
        {{ trigger.payload_json.error.message }}
```

Run this while you build a new payload. It also catches HTTP commands from other tools.

## Show the screen on a dashboard

Publish anything to `<P>/cmd/screen/get`. The reply on `<P>/state/screen` is `{"width","height","pixels"}`, row by row, each pixel a decimal `0xRRGGBB`. It excludes brightness and the display color settings. This trigger-based template sensor turns each reply into an SVG picture:

```yaml
template:
  - triggers:
      - trigger: mqtt
        topic: "<P>/state/screen"
    sensor:
      - name: Clock screen
        unique_id: clock_screen
        state: "{{ trigger.payload_json.width }}x{{ trigger.payload_json.height }}"
        picture: >-
          {% set p = trigger.payload_json %}
          {%- set w = p.width | int(32) -%}
          {%- set ns = namespace(r='') -%}
          {%- for c in p.pixels -%}
          {%- if c | int(0) > 0 -%}
          {%- set ns.r = ns.r ~ "<rect x='" ~ (loop.index0 % w) ~ "' y='" ~ (loop.index0 // w) ~ "' width='1' height='1' fill='#" ~ ('%06x' | format(c | int)) ~ "'/>" -%}
          {%- endif -%}
          {%- endfor -%}
          {%- set svg = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 " ~ w ~ " " ~ (p.height | int(8)) ~ "' shape-rendering='crispEdges'><rect width='100%' height='100%' fill='#000'/>" ~ ns.r ~ "</svg>" -%}
          {{ 'data:image/svg+xml,' ~ (svg | urlencode) }}

recorder:
  exclude:
    entities:
      - sensor.clock_screen
```

- Show it with a markdown card holding `<img src="{{ state_attr('sensor.clock_screen', 'entity_picture') }}">`. A picture-entity card reports no image source.
- The recorder exclude matters: a frame is many kilobytes of attributes, and the recorder refuses attributes over 16 KB and logs a warning for each. It takes effect after an HA restart.
- For a live view, publish to `cmd/screen/get` from a `time_pattern` trigger every few seconds, gated by a helper, with a second automation that turns the helper off after some minutes. Polling forever wastes traffic and memory.

## Writing good content

- Only a handful of characters fit: about 8 on a 32-pixel display, about 6 at double size, and fewer beside an icon. Short values read best; use `repeat: 1` for anything longer.
- Cut free text from a calendar or a media player before you send it: `{{ title[:20] ~ '...' if title | length > 20 else title }}`.
- Keep effects slow (`effectSpeed` 0.2 to 0.5) and text white or pale. An effect cannot be dimmed.
- Give one thing a fixed look across automations, for example a color per severity, so the display can be read at a glance.
- Use an overlay for weather and leave the background free. Overlays keep the text readable.
- Use `"stack": false` when a new message makes the current one pointless.
