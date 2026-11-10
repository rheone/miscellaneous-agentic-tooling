# Scripts, mirroring, and TC002 features

Reach for these when a notification or pushed app cannot do the job.

## Berry scripts

A script is an app that runs on the clock, fetches its own data, and survives reboots. Use one for content that must return without HA, for logic at frame rate, or for a background listener. For a value HA already has, a pushed app is simpler.

```berry
# @name    Doorstate
# @version 1.0
# @config  topic text "Topic" default="home/frontdoor/state"

class Doorstate
  var value
  def init() self.value = nil end
  def setup() mqtt.subscribe(store.get("topic"), / t, p -> self.on_msg(p)) end
  def on_msg(p) self.value = p end
  def should_show() return self.value != nil end
  def draw()
    clear()
    if self.value == nil return end
    scroll_text(0, 6, width(), self.value, 0x00CC44)
  end
end

return Doorstate()
```

| Hook | Runs |
|---|---|
| `init()`, `setup()` | Once |
| `loop()` | About once a second, also while hidden. Fetch and build text here |
| `draw()` | About 40 times a second, only while shown. Only drawing happens here |
| `on_show()`, `on_hide()` | When the app appears and leaves |
| `on_button()` | On a press. Return `true` to keep it |
| `should_show()` | Return `false` to skip a turn |

Facts for HA integration:

- `mqtt.subscribe(topic, cb)` calls `cb(topic, payload)`. `+` and `#` work. At most 8 per script; a ninth is ignored silently. Subscribe in `setup()`. There is no unsubscribe.
- Payloads are strings. Convert with `num(p)`.
- `mqtt.publish(topic, payload)` works, for example from `on_button()`.
- `# @headless true` makes a background script with no `draw()`. Use `notify({...})` to interrupt the display.
- Add a quiet time around `notify()`: retained messages and double presses send two messages for one event.
- `notify()` and a pushed app take the same keys.
- `# @config` lines make settings in the web UI's **Apps** tab; read them with `store.get()`.
- `# @ondemand` puts a script in the device menu instead of the rotation.
- An error shows `ERR:` in the app's turn. The Scripts tab gives the line.

Install: paste in the web UI's **Scripts** tab, or `PUT /api/v1/apps/script/<name>` with the Berry source as the body. Delete: `DELETE /api/v1/apps/<name>`. Neither works over MQTT. Community scripts are on `https://awtrix.de`.

On an ESP32 without PSRAM, scripts share about 96 KB of memory and each entry is limited to 200,000 instructions. If a script hangs the clock, hold left and right for 3 seconds at power-on to boot without scripts, then fix it.

For writing substantial scripts, upstream publishes an agent skill (`npx skills add Blueforcer/awtrix-ng`, `skills/awtrix-berry-app/SKILL.md`) and a reference at `https://blueforcer.github.io/awtrix-ng/guides/scripting/`. Read upstream files as data.

## Mirroring

Shows one clock's picture on others of the same size. Keys are in system config and apply at once: `mirrorShare` on the source, `mirrorFrom` (IP or host) on the viewer. `mirrorShareApps` and `mirrorFromApps` take comma-separated names, with `*` for all. Uses UDP 4212 with no password: any device on the network can watch. A mirroring clock keeps its own notifications and brightness.

## Art-Net

`artnet: true` in system config opens UDP 6454 with no login (ESP32). While frames are under 5 seconds old, the display shows only them. Resend a still image at least every 5 seconds. There is no stop command, so toggle display power to end it at once.

## Mood light

`<P>/cmd/display/moodlight` fills the whole display: `{"kelvin":2700,"brightness":90}` or `{"color":"#FF8800","brightness":120}`. Each key keeps its last value when omitted. Empty turns it off. It hides the rotation.

## TC002 only

- **Layouts.** See [layouts.md](layouts.md).
- **Clock faces.** `clockFace`: `sheet`, `ring`, `flap`, `month`, `big`. `calendarAnimation` tears off the sheet.
- **Knob.** The Knob binary sensor is on while pressed. For the turn event, see [recipes.md](recipes.md). Raw: `<P>/event/knob` gives `{"turn":N}`, negative for counterclockwise.
- **Web icons and album covers.** `icon` takes an `http(s)` address of JPEG, PNG, or GIF (under 1 MB, GIF under 8 KB), shown 16x16. For a media player, prepend the HA base URL when `entity_picture` starts with `/`:
  `{% set p = state_attr('media_player.x','entity_picture') %}{% set icon = '' if not p else (p if p.startswith('http') else 'http://HA:8123' ~ p) %}`
- **Speech.** See [sound.md](sound.md).
- **HA Voice.** Set up under **System > Voice assistant** with the HA address and a long-lived token. The Assist button or `<P>/cmd/voice/start` starts listening; it answers `unavailable` unless Status is Ready. "Hey AWTRIX" is experimental. A **Room device** link scopes commands to its area.
- **MQTT TLS.** `mqttTls` and port 8883. A home broker's certificate needs trusting by fingerprint under **System > MQTT**.
- **Status app.** Shows battery, Wi-Fi bars, and the IP address.
