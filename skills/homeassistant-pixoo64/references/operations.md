# Sending pages and running the device

## Contents

- [Entities](#entities)
- [Actions](#actions)
- [`duration` and the page rotation](#duration-and-the-page-rotation)
- [Screen and brightness](#screen-and-brightness)
- [A reusable display script](#a-reusable-display-script)
- [Connection, API fallback and errors](#connection-api-fallback-and-errors)
- [Rate and stability](#rate-and-stability)

## Entities

Each configured Pixoo gets two entities on one device. Their ids follow the device name (default title "Divoom Pixoo 64"), and users often rename them, so look them up (`ha_search "pixoo"`, or the device page) instead of guessing.

| Entity | Typical id | State |
|---|---|---|
| Sensor "Current Page" | `sensor.divoom_pixoo_64_current_page` | 1-based index of the rotation page now shown. Attribute `TotalPages` = number of pages in `pages_data`. **Every `divoom_pixoo.*` action targets this entity.** |
| Light "Light" | `light.divoom_pixoo_64_light` | Screen on/off and brightness. Brightness only, no color. |

Both turn `unavailable` when the light's poll (`Channel/GetAllConf`) fails.

## Actions

| Action | Fields | Notes |
|---|---|---|
| `divoom_pixoo.show_message` | `page_data` (required), `duration` (whole seconds; the UI offers 1-9999, the action also takes 0, which moves the rotation on at once) | Draws one page now. |
| `divoom_pixoo.update_page` | none | Draws the current rotation page again. Fails when the integration has no rotation pages. Calling it many times in a row can crash the device. |
| `divoom_pixoo.restart` | none | Reboots the device (`Device/SysReboot`). Takes a while. |
| `divoom_pixoo.play_buzzer` | `buzz_cycle_time_millis` (500), `idle_cycle_time_millis` (500), `total_time` (3000) | Upstream warns it could damage the device. Ask the user before you use it. |

```yaml
action: divoom_pixoo.show_message
target:
  entity_id: sensor.divoom_pixoo_64_current_page
data:
  duration: 15
  page_data:
    page_type: components
    components: [...]
```

`show_message` blocks until the frame is sent. If the device does not answer, the action **raises a raw connection error** and stops the automation. `continue_on_error: true` does not help: Home Assistant only ignores its own error types. When the Pixoo is optional to an automation, check that the sensor is not `unavailable`, and run the Pixoo steps in a script started with `script.turn_on` (fire and forget), so a failure stops only that script.

## `duration` and the page rotation

The integration can rotate through pages set in its options (`pages_data`, each shown for `scan_interval` seconds or its own `duration`). `show_message` interacts with it:

| Rotation | After `show_message` |
|---|---|
| Has pages (`TotalPages` > 0) | The message stays for `duration` seconds (default `scan_interval`), then the rotation continues with the next page. |
| No pages | The message stays until something else draws. `duration` does nothing. |

Check `TotalPages` before you rely on either behavior. Known bug (#167): if every rotation page is disabled, the rotation stops. It restarts after you enable a page and then call `show_message`, or reload the integration.

`clock`, `channel`, `visualizer` and `gif` switch the device to its own content; a later `components` page switches it back.

## Screen and brightness

- `light.turn_on` with `brightness` or `brightness_pct` sets the brightness (0-100 % on the device) and turns the screen on. Without brightness it only turns the screen on.
- `light.turn_off` turns the screen off. The device still accepts pages while off; they are not visible until the screen turns on.
- To avoid a flash of the old content, send the page first, then turn the screen on.
- To leave the display as you found it, record whether the light was on before, and turn it off afterwards only if it was off.

## A reusable display script

First look for a display script the configuration already has (search scripts for `divoom_pixoo.show_message`), and send through it; use this design only when there is none, or as a checklist to improve the existing one.

When many automations show pages, give them one script. This design avoids the usual problems: pages dropped while another one shows, text placed at fixed rows that do not fit the font, and a screen turned off that the user had turned on.

```yaml
pixoo_show:
  alias: Pixoo show page
  mode: queued              # pages wait their turn instead of being dropped
  max: 10
  fields:
    page_data: {description: "A complete, linted page_data mapping", required: true, selector: {object: {}}}
    seconds: {default: 15, selector: {number: {min: 3, max: 300}}}
    brightness_pct: {default: 60, selector: {number: {min: 5, max: 100}}}  # used only when the screen was off
  variables:
    light: light.divoom_pixoo_64_light            # replace with the real ids
    sensor: sensor.divoom_pixoo_64_current_page
    was_on: "{{ is_state(light, 'on') }}"
  sequence:
    - condition: template                         # skip quietly while the device is offline
      value_template: "{{ states(sensor) not in ['unavailable', 'unknown'] }}"
    - action: divoom_pixoo.show_message
      target: {entity_id: "{{ sensor }}"}
      data:
        page_data: "{{ page_data }}"
        duration: "{{ seconds }}"                 # rotation resumes when the page is done
    - if: "{{ not was_on }}"                       # keep the user's brightness when the screen is already on
      then:
        - action: light.turn_on
          target: {entity_id: "{{ light }}"}
          data: {brightness_pct: "{{ brightness_pct }}"}
    - delay: {seconds: "{{ seconds }}"}
    - if: "{{ not was_on }}"
      then:
        - action: light.turn_off
          target: {entity_id: "{{ light }}"}
```

Design notes:

- Callers pass a whole page that was designed and linted with `pixoo.py`. A script that builds "header, body, footer" at fixed rows cannot know the font or the text length, so it overflows; if you want one, measure its slots with `suggest --stable` and document the character budget of each slot.
- `mode: queued` replaces a separate "busy" helper and a wait loop.
- Put quiet hours and urgency checks in the script, not in every caller.
- Keep a safety automation that turns the screen off after some minutes, in case a run is cut short by a restart:

  ```yaml
  alias: "Pixoo: safety auto-off"
  mode: single
  triggers:
    - trigger: state
      entity_id: light.divoom_pixoo_64_light
      to: "on"
      for: {minutes: 10}
  actions:
    - action: light.turn_off
      target: {entity_id: light.divoom_pixoo_64_light}
  ```

  If some pages must stay up longer (a ringing alarm), add a condition on a "busy" helper the display script sets, so the cutoff leaves them alone.

## Connection, API fallback and errors

- Every command is an HTTP POST with a 9 s timeout. 1.24.0 tries `http://<ip>/post` first. On a connection error or timeout it tries `http://<ip>:9000/divoom_api` After port 9000 has answered once, it uses only port 9000 until the integration entry reloads or Home Assistant restarts; while port 80 works, every failure tries both again. There is no option for the port.
- The fallback only changes the address. Newer firmware (Pixoo 64 II) also answers in another format (`ReturnCode` instead of `error_code`) and lacks `Draw/GetHttpGifId`, so setup can still fail with "Unable to connect" or `KeyError: 'error_code'` (open issues #163, #168).
- A device that is off the network costs up to 18 s per command (two timeouts) and makes both entities unavailable.
- Setup discovery asks Divoom's cloud (`app.divoom-gz.com`) for devices on the same network. Without internet, enter the IP by hand.
- Give the Pixoo a fixed IP (DHCP reservation): the integration stores the IP, not a device id.

## Rate and stability

- Each `components` page is one frame (`Draw/SendHttpGif`). The integration resets the device's frame counter every 32 frames to avoid the known freeze after many frames.
- Send at most one page every few seconds; rapid `update_page` or `show_message` calls can crash the device. For animation, use a `gif` page.
- `show_message` renders its templates once, so a time or value on the page is frozen while it shows. For a live clock use a `clock` page, or send the page again each minute.
- Some users report the device stops answering on port 80 after long use while still answering ping (issue #153). A power cycle or `divoom_pixoo.restart` recovers it.
- `image_url` is downloaded at every draw. Prefer local files in `/config/www` for pages that repeat.
