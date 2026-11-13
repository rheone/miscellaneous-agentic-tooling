# Device settings

Two stores, on purpose:

| Store | Route | MQTT | Applies | Examples |
|---|---|---|---|---|
| **Settings** | `PATCH /api/v1/settings` | `<P>/cmd/settings` | At once, no restart | Brightness, colors, clock look, transitions, volume |
| **System config** | `PUT /api/v1/system` | None, HTTP only | Many need a reboot | Wi-Fi, MQTT, time zone, hostname, login, calibration |

Settings reject unknown keys with `422`. **System config accepts an unknown key with `200` and discards it**, so check the returned object for a typo. Secrets (`mqttPass`, `authPass`) are left out of reads; an empty value keeps the stored one.

## Find a clock

Once the clock is in HA, read its **IP address** sensor. Otherwise: the display shows the address at start-up, the router lists it, or use `http://<hostname>.local` (default `awtrixng-` plus the last 6 MAC characters). Clocks announce `_awtrixng._tcp` over mDNS, and answer the text `FIND_AWTRIXNG` broadcast to UDP 4210, replying to UDP 4211. Router client isolation blocks the UDP search.

## Settings keys

| Group | Keys (default) |
|---|---|
| Brightness | `brightness` (120, 0-255, not percent), `autoBrightness` (false) |
| Text | `textColor` (#FFFFFF), `uppercase` (true), `scroll` (object, see [payload.md](payload.md)) |
| Rotation | `autoTransition` (true), `appDurationMs` (7000), `transitionEffect` (Rain), `transitionDirection` (normal), `transitionDurationMs` (1000) |
| Clock | `timeMode` (1), `timeColor` (null), `time24h` (true), `timeLeadingZero` (true), `timeShowSeconds` (false), `timeShowAmPm` (false), `timeSeparatorMode` (`pulse`; `steady`, `blink`) |
| Calendar box | `calendarHeaderColor` (#FF0000), `calendarTextColor` (#000000), `calendarBodyColor` (#FFFFFF) |
| Date app | `dateOrder` (`dayMonthYear`, `monthDayYear`, `yearMonthDay`), `dateSeparator` (`dot`, `slash`, `dash`), `dateYearMode` (`none`, `twoDigit`, `fourDigit`), `dateShowWeekday` (false), `dateMonthNames` (false), `dateColor` (null) |
| Weekday bar | `weekdayBar`, `dateWeekdayBar`: `show`, `startOnMonday` (true), `weekendDays` (lowercase names), `activeColor`, `inactiveColor`, `weekendActiveColor`, `weekendInactiveColor` |
| Sensor apps | `useCelsius` (true), `temperatureColor`, `humidityColor`, `batteryColor` (null) |
| Color | `saturation` (100), `gamma` (1.9), `colorCorrection`, `colorTint` (null) |
| Sound | `volume`, `alertVolume`, `appVolume`, `radioVolume` |
| Buttons | `blockNavigation` (false) |
| TC002 only | `clockFace` (`sheet`), `calendarAnimation` (true), `enlargeApps` (true), `bootSound` (true), `musicSource` (`auto`, `playback`, `microphone`) |

A `null` optional color means use `textColor`. Integer keys refuse decimals.

### `timeMode` (ESP32 clocks)

| Value | Style |
|---|---|
| 0 | Time centered, full-width weekday bar |
| 1 | Calendar box, top bar, weekday bar bottom |
| 2 | Like 1, weekday bar top |
| 3 | Calendar box with notched corners, bar bottom |
| 4 | Like 3, bar top |
| 5 | Big black digits on color. `timeColor` is the background |
| 6 | Binary: hours red, minutes green, seconds blue |

Modes 1 to 4 have no room for seconds or AM/PM.

## Device state fields

From `<P>/state/device` or `GET /api/v1/device`:

| Field | Use |
|---|---|
| `version`, `uid`, `macAddress`, `ipAddress`, `hostname`, `boardType`, `soc` | Identity |
| `uptimeSeconds` | Falls to near 0 after a restart, when pushed apps are gone |
| `resetReason` | `panic`, a `watchdog` value, or `brownout` after a crash or power problem. `software` is a normal restart. Worth an alert |
| `freeHeapBytes`, `minFreeHeapBytes` | A `minFreeHeapBytes` that keeps dropping over days points to a leak |
| `largestFreeBlockBytes` | The one that matters when "not enough memory" appears despite free heap |
| `scriptingRunning` | Whether scripts run |
| `fps` | Frames shown per second |
| `brightness` | The level in use right now, not the stored setting |
| `matrixPower`, `currentApp`, `indicators` | A notification does not change `currentApp` |
| `messageCount` | MQTT commands received since start |
| `wifi`, `mqtt` | `state`, `host`, `endpoint`, `attempts`, `connects`, `error`, `lastError` |
| `mirror` | Mirroring state |
| `lightLevel`, `ldrRaw`, `temperature`, `humidity`, `pressureHpa`, `battery*`, `lowBattery`, `usbPower`, `psram*` | Present only with that hardware |

## Built-in apps

ESP32: `Time`, `Date`, `Temperature`, `Humidity`, `Battery`. An app needing absent hardware does not exist. A built-in app cannot be deleted; switch it off with `<P>/cmd/apps/<name>/enabled`. TC002: `Time`, `Status`.

The default order is built-ins, pushed apps by first arrival, then scripts. Rotation runs only with at least two apps.

## Buttons on the clock

| Button | Default action |
|---|---|
| Left, right | Previous, next app |
| Select, once | Dismiss the notice shown |
| Select, twice quickly | Display off or on |
| Select, held 0.5 s | Menu of on-demand scripts |
| Left + right, held at power-on 3 s | Boot without scripts (`NOSCR`). ESP32 |
| Select held at power-on 1 s | Setup hotspot (`SETUP`). ESP32 |

`blockNavigation` stops left, right, double press, and the menu. One press of select still dismisses, and MQTT and scripts still see presses. `buttonCallback` (system config) POSTs presses to an `http://` URL, but MQTT already reports them. A slow listener freezes the display for up to about 0.6 s per event on ESP32, so prefer MQTT.

## Auto-brightness

System config, applied at once: `minBrightness` (10), `maxBrightness` (220), `ldrGamma` (2.2), `ldrFactor`, `ldrOnGround`, `brightnessSmoothing` (10000 ms). With the defaults, 50 percent room light gives brightness 56.

| Problem | Change |
|---|---|
| Too dark at night | Raise `minBrightness` |
| Too bright by day | Lower `maxBrightness` |
| Bright too early at dusk | Raise `ldrGamma` |
| Pulses with a TV | Raise `brightnessSmoothing` |
| Never gets bright | Raise `ldrFactor` (check `lightLevel`) |
| Backwards | `ldrOnGround: true` |

`brightness` in `state/device` is what the display really uses. The tuning keys are refused by `cmd/settings` as unknown fields.

## Sensors and battery

Temperature, humidity, and pressure are auto-detected at boot (BME280, BMP280, HTU21DF, SHT31). `tempOffset` defaults to `-9.0` on ESP32, for a sensor beside the LEDs. To calibrate, set `tempOffset` to reference minus reported. It stays in Celsius even in Fahrenheit display.

Battery percent is estimated from voltage, so it drops under load and recovers. If voltage reads wrong, fix `batteryDividerRatio` (1.79 default), calculated as `4.2 / (batteryPinMillivolts / 1000)` on a full battery. `lowBatteryThreshold` is 0 (off) by default.

## Power

| Action | Effect |
|---|---|
| Display off (`cmd/display` or the Matrix light) | LEDs only. Wi-Fi, MQTT, apps keep running |
| Deep sleep (`cmd/device/sleep`) | Unreachable for `durationMs`, cannot be cancelled. The timer or select wakes it, as a fresh start. Pushed apps are lost |

## Time

`tz` (POSIX string; not checked, a bad value gives wrong time), `tzName` (a label only), `ntpServer`. All apply at once. The web UI picker sets both zone keys correctly.

```json
{"tz":"EST5EDT,M3.2.0,M11.1.0","tzName":"America/New_York"}
```

## Resets and firmware

| Action | Clears | Keeps |
|---|---|---|
| Settings reset (`cmd/settings/reset`) | Settings, then restarts | System config, files |
| Factory reset (HTTP only, no confirmation) | Settings, system config, Wi-Fi, all files | Nothing |

Confirm with the user before any reset, deep sleep, or firmware change. Firmware update: web UI **System > Maintenance > Check for updates**, or `curl -X POST http://<ip>/update -F "firmware=@firmware-awtrix-ng.bin"` on ESP32. Settings and files stay. The clock refuses an image for another chip. The `usb-*.bin` files are for first install only.

## Backup

Web UI **System > Backup & restore** builds a `.zip` in the browser, with Wi-Fi, settings, icons, melodies, palettes, scripts, and app order as options. Radio stations and MP3s are options on clocks that have them. Pushed apps are not included, because they live in memory.

A backup that includes Wi-Fi or settings contains your Wi-Fi, MQTT, and web login passwords, so store it like a secret. Restore with the web UI or `curl -X POST http://<ip>/api/v1/restore -F "file=@backup.zip"`, which also works in setup mode. Reboot afterward for Wi-Fi and system config to apply. A restore runs file by file, so a stop halfway leaves the earlier files changed.

## Login and security

`authEnabled`, `authUser`, `authPass` apply at once and protect the whole web UI and HTTP API. Default is off: until set, anyone on the network can change files and config, and `GET /api/v1/system?secrets=1` returns the Wi-Fi, MQTT, and login passwords. Turn the login on, and give the clock its own limited broker user. `mqttUser` is returned in reads; `mqttPass` is not, without `?secrets=1`. A change to the broker password needs a reboot of the clock.

## Other system keys

`hostname`, `webPort` (reboot), `statsInterval` (1000 to 600000, reboot), `swapButtons`, `scriptingEnabled` (reboot), `wifiRoamRssi` (0 off; -75 is a good start on a mesh), `debugMode`, `tempDecimals`.
