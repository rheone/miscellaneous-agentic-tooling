# Lessons from real Pixoo configurations

Collected on 2026-11-08 by linting 68 Pixoo pages in one working Home Assistant setup (automations and scripts written by people and agents over several months, many before 1.24.0). These are the mistakes that really happen, most common first.

| Seen | Mistake | Lesson |
|---|---|---|
| 40 pages | Templates with no way to check them | Every templated page needs worst-case samples. A page that was only ever tested with one short value overflows with the long one. |
| 15 texts | Text wider than 64 px | Mostly capital-only fonts (`gicko`, `eleven_pix`) with words of 10+ letters, and labels written before anyone measured. Measure every fixed string; size every slot for its worst case. |
| 12 images | `align: center` on images | Copied from an old example. It has no effect: `position` is the top-left corner. Examples spread mistakes, so keep examples linted. |
| 12 texts | Text over an image with no backdrop | Contrast cannot be checked and varies by image. Put a dark filled rectangle behind the text, or keep text off the image. |
| 4 pages | A separate "TEST" page that differs from the real one | Test branches drew a banner over the title (overlapping by 23 px) and so never tested the real layout. Test with an event that feeds sample values into the same page code. |
| 3 texts | Symbols the font lacks: `!` in `pix24`, `+` and `%` in `eleven_pix` | Nothing is drawn and the text shifts. `coverage` before you pick a big font; draw a missing sign another way. |
| 1 image | Image path that does not exist | Nothing is drawn, no visible error. Check the file before you reference it. |
| 1 text | Light gray on light blue (2.1:1) | Mid-tone pairs look fine in a browser and wash out on LEDs. Keep 3:1 or more. |
| several | `\|` block text with a trailing newline (`"Coop the\nchickens\n"`) | Harmless, but adds an empty line; use `\|-`. |
| several | Pages that relied on upper case | After 1.24.0, mixed-case text in `pico_8` shows small capitals and in the new BDF fonts real lower case (`five_pix` still looks like capitals). Decide the case on purpose (`\| upper`). |

Seen while testing on the device:

- **Presence-triggered pages replace a test page when you walk up to photograph it.** Pause them, or hold the display, while you test.
- **A shared "busy" helper needs one owner.** When every display run turns it off at its end, it no longer protects a page someone else is holding, and a queue that waits with a timeout carries on anyway.

Patterns that worked well in the same setup:

- **One queued display script** that every caller uses: pages wait their turn instead of being dropped. A separate "busy" helper lets a safety auto-off leave a page alone while it shows.
- **A Pixoo-only quiet-hours switch** with an `urgent` override, separate from the house-wide one.
- **An availability check** before any Pixoo call, so an offline display never stops an automation.
- **A brightness helper** the user controls, read by the display script, instead of brightness numbers in every automation.
- **Test events per automation** (`event_type: pixoo_test_<name>`), so a page can be shown on demand. Best when the event only supplies sample data to the real page.
- **The same alert on two displays** (Pixoo and a second LED clock) built from one set of values, so the two never disagree.
