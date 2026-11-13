# Verification checklist

Use it before you send a page (or save an automation that sends one), and again after. Report to the user which items you checked with the tools, which on Home Assistant, and which only the user can check on the device.

## Before sending

Design:

- [ ] Both entity ids come from Home Assistant (`ha_search "pixoo"`), not from an example.
- [ ] Every text component's font and `position` come from `suggest` or `measure`.
- [ ] `coverage` shows `all drawn` for every character of every text, including the worst-case samples of templated text.
- [ ] Every templated value has a written list of worst cases (longest, widest, negative, `unavailable`, one line and two lines).
- [ ] `render` was run once per worst case, with a `--fill` sample for every template: no ERROR, no WARNING, no `not-checked`.
- [ ] You Read the PNG of at least the widest case: nothing touches, the most important item is the biggest, text over images has a backdrop.

YAML details the tools also flag, worth a second look:

- [ ] Colors are lower-case CSS4 names or `[R, G, B]` with whole numbers.
- [ ] Every rectangle states `filled: true` or `filled: false`.
- [ ] Every image file exists under `/config/www`, is 64 px or smaller, and pixel art uses `resample_mode: nearest`. Images have no `align`.
- [ ] Numbers share their `content` with a unit or other text.
- [ ] `page_type` is spelled as in [pages](pages.md#page-types).

Sending:

- [ ] The page goes through the configuration's existing display script, if it has one.
- [ ] The offline case is handled: the sensor is checked for `unavailable`, and the Pixoo steps run in a script started with `script.turn_on`, so a dead device stops only that script.
- [ ] `duration` matches the rotation: with `TotalPages` > 0 the rotation returns after it; with none, the page stays.
- [ ] The screen and brightness are left as found (turned off afterwards only if they were off).
- [ ] You asked the user how long the page should show if they did not say.

## After sending

- [ ] The action or script run finished without an error (read its trace).
- [ ] The Home Assistant log has no new `divoom_pixoo` lines: `Unknown font`, `Template render error`, `Error rendering page`, `KeyError`.
- [ ] The sensor is not `unavailable`.
- [ ] The user confirmed the page on the device matches the PNG, or you told them it is not yet confirmed. The tools model the integration's code; only the device shows the real LEDs.
- [ ] After an integration update, or when a page looks different from its preview: show [examples/calibration.yaml](../examples/calibration.yaml) and compare a photo with its render. Pause presence-triggered pages first, or they replace it while you walk up to look.
