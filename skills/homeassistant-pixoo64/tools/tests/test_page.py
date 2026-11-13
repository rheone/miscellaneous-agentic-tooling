import glob
import io
import json
import os
import struct
import tempfile
import unittest
import zlib
from contextlib import redirect_stdout

from _base import SKILL, src
from pixoo_kit import cli, page as P, png


def rules(page, **kw):
    return {(f.rule, f.severity) for f in P.render(src(), page, **kw).findings}


def comps(*c):
    return {"page_type": "components", "components": list(c)}


class ColorTests(unittest.TestCase):
    def test_colour_rules(self):
        self.assertIn(("color-unknown", "error"), rules(comps({"type": "text", "content": "A", "position": [0, 0], "color": "Red"})))
        self.assertIn(("color-unknown", "error"), rules(comps({"type": "text", "content": "A", "position": [0, 0], "color": "#ff0000"})))
        self.assertFalse(any(r[1] == "error" for r in rules(comps({"type": "text", "content": "A", "position": [0, 10], "color": [255, 0, 0]}))))

    def test_contrast(self):
        page = comps({"type": "text", "content": "DARK", "position": [32, 10], "align": "center", "color": [0, 0, 255]})
        self.assertIn(("contrast", "warning"), rules(page))


class ComponentTests(unittest.TestCase):
    def test_rectangle_defaults_to_filled(self):
        r = P.render(src(), comps({"type": "rectangle", "position": [0, 0], "size": [4, 4]}))
        self.assertEqual(sum(1 for row in r.owner for o in row if o == 0), 16)
        self.assertIn("rect-filled-default", {f.rule for f in r.findings})

    def test_outline_rectangle(self):
        r = P.render(src(), comps({"type": "rectangle", "position": [0, 0], "size": [4, 4], "filled": False}))
        self.assertEqual(sum(1 for row in r.owner for o in row if o == 0), 12)

    def test_overlap(self):
        page = comps({"type": "text", "content": "AAAA", "position": [32, 10], "align": "center"},
                     {"type": "text", "content": "BBBB", "position": [32, 12], "align": "center"})
        self.assertIn(("text-overlap", "warning"), rules(page))

    def test_shadow_effect_is_info(self):
        page = comps({"type": "text", "content": "HI", "position": [33, 11], "align": "center", "color": "gray"},
                     {"type": "text", "content": "HI", "position": [32, 10], "align": "center"})
        self.assertIn(("text-effect", "info"), rules(page))
        self.assertNotIn(("text-overlap", "warning"), rules(page))

    def test_image_align_ignored(self):
        page = comps({"type": "image", "image_url": "http://x/y.png", "position": [0, 0], "align": "center"})
        self.assertIn(("key-ignored", "warning"), rules(page))

    def test_text_position_template_in_config(self):
        page = comps({"type": "text", "content": "A", "position": ["{{ 3 }}", 0]})
        self.assertIn(("text-position-templated", "error"), rules(page, context="config"))
        self.assertNotIn(("text-position-templated", "error"), rules(page, context="service"))

    def test_templated_text_fill(self):
        page = comps({"type": "text", "content": "{{ x }}", "position": [32, 0], "align": "center", "font": "pix24"})
        self.assertIn(("text", "error"), rules(page, fill="-5"))  # pix24 has no minus


class PageTests(unittest.TestCase):
    def test_visualiser_spelling(self):
        self.assertIn(("page-type-unknown", "error"), rules({"page_type": "visualiser", "id": 0}))

    def test_variables_in_service_call(self):
        self.assertIn(("variables-in-service", "warning"), rules({"page_type": "components", "variables": {"a": 1}, "components": []}))

    def test_progress_must_be_a_number(self):
        page = {"page_type": "progress_bar", "header": "a", "footer": "b"}
        self.assertIn(("progress-int", "info"), rules(dict(page, progress=45.5)))      # int(45.5) = 45
        self.assertIn(("progress-int", "error"), rules(dict(page, progress="unavailable")))

    def test_native_types(self):
        self.assertEqual(P.ha_native("11.10"), 11.1)
        self.assertEqual(P.ha_native("007"), "007")       # leading zero stays text
        self.assertEqual(P.ha_native("1e3"), "1e3")
        self.assertEqual(P.ha_native("+5"), 5)
        self.assertEqual(P.ha_native("[255,0,0]"), [255, 0, 0])
        self.assertIs(P.ha_native("False"), False)
        self.assertEqual(P.ha_native("false"), "false")
        page = comps({"type": "text", "content": "11.10", "position": [32, 10], "align": "center"})
        self.assertIn(("text-native-type", "warning"), rules(page))

    def test_color_string_list_and_floats(self):
        ok = comps({"type": "text", "content": "A", "position": [0, 10], "color": "[255,0,0]"})
        self.assertFalse(any(r[1] == "error" for r in rules(ok)))
        bad = comps({"type": "text", "content": "A", "position": [0, 10], "color": [255, 127.5, 0]})
        self.assertIn(("color-float", "error"), rules(bad))
        tup = comps({"type": "text", "content": "A", "position": [0, 10], "color": "(255, 0, 0)"})
        self.assertIn(("color-unknown", "error"), rules(tup))

    def test_filled_strings_follow_native_types(self):
        def cells(filled):
            r = P.render(src(), comps({"type": "rectangle", "position": [0, 0], "size": [4, 4], "filled": filled}))
            return sum(1 for row in r.owner for o in row if o == 0)
        self.assertEqual(cells("0"), 12)       # parsed to 0 -> outline
        self.assertEqual(cells("False"), 12)   # parsed to False -> outline
        self.assertEqual(cells("false"), 16)   # stays text -> filled
        self.assertEqual(cells(False), 12)

    def test_outline_one_pixel_draws_nothing(self):
        r = P.render(src(), comps({"type": "rectangle", "position": [5, 5], "size": [1, 1], "filled": False}))
        self.assertEqual(sum(1 for row in r.owner for o in row if o == 0), 0)

    def test_find_pages_nested(self):
        tree = [{"alias": "My alert", "actions": [{"action": "divoom_pixoo.show_message",
                                                   "data": {"page_data": {"page_type": "clock", "id": 1}}}]}]
        found = P.find_pages(tree)
        self.assertEqual(len(found), 1)
        self.assertIn("My alert", found[0][0])


# Worst-case samples per example: every run must be free of errors and warnings.
EXAMPLE_SAMPLES = {
    "notification.yaml": [["3=23:59"]],
    "status-list.yaml": [[]],
    "progress.yaml": [[]],
    "device-pages.yaml": [[]],
    "calibration.yaml": [[]],
    "image-with-label.yaml": [["2=Feed the cats"], ["2=Water the plants"]],
    "alarm-bell.yaml": [["16=07:30", "17=Wake up"], ["16=23:59", "17=Pills"]],
    "sensor-value.yaml": [
        ["2=28.8°", "1.position=2,24", "4=Humidity 100%"],   # widest value (minus at 52 - 42 - 8)
        ["2=1.1°", "1.position=19,24", "4=Humidity 0%"],     # narrowest value
    ],
}


class ExampleTests(unittest.TestCase):
    def test_examples_have_no_errors_or_warnings(self):
        files = sorted(glob.glob(os.path.join(SKILL, "examples", "*.yaml")))
        self.assertEqual({os.path.basename(f) for f in files}, set(EXAMPLE_SAMPLES), "every example needs samples")
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML not installed")
        for path in files:
            for where, pg in P.find_pages(cli._load_any(path)):
                for samples in EXAMPLE_SAMPLES[os.path.basename(path)]:
                    bad = [f for f in P.render(src(), pg, fill=samples).findings if f.severity != "info"]
                    self.assertEqual(bad, [], f"{os.path.basename(path)} {where} {samples}")

    def test_unfilled_template_is_a_warning(self):
        page = comps({"type": "text", "content": "{{ name }} is open", "position": [32, 30], "align": "center"})
        self.assertIn(("not-checked", "warning"), rules(page))
        self.assertIn(("not-checked-summary", "warning"), rules(page))

    def test_per_component_fill(self):
        page = comps({"type": "text", "content": "{{ name }} is open", "position": [32, 30], "align": "center",
                      "font": "gicko"})
        self.assertIn(("text", "error"), rules(page, fill=["0=Kid's Room (Window) is open"]))


class SpriteTests(unittest.TestCase):
    def test_runs_merge_into_rectangles(self):
        rects = cli.sprite_rects("##.\n##.\n.#o\n", 10, 20, {"#": "gold", "o": "white"}, 1)
        self.assertIn({"type": "rectangle", "position": [10, 20], "size": [2, 2], "color": "gold", "filled": True}, rects)
        self.assertEqual(len(rects), 3)
        r = P.render(src(), comps(*rects))
        self.assertEqual(sum(1 for row in r.owner for o in row if o >= 0), 6)

    def test_scale(self):
        rects = cli.sprite_rects("#", 0, 0, {"*": "white"}, 3)
        self.assertEqual(rects[0]["size"], [3, 3])


class OutputTests(unittest.TestCase):
    def test_png_is_valid(self):
        r = P.render(src(), comps({"type": "text", "content": "Hi", "position": [32, 30], "align": "center"}))
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "p.png")
            png.write(path, r.pixels, scale=2, led=False)
            with open(path, "rb") as fh:
                data = fh.read()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", data[16:24]), (128, 128))
        idat = data.index(b"IDAT")
        (length,) = struct.unpack(">I", data[idat - 4:idat])
        self.assertEqual(len(zlib.decompress(data[idat + 4:idat + 4 + length])), 128 * (1 + 128 * 3))

    def test_cli_json(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            cli.main(["--vendored", "suggest", "Hello", "--json"])
        data = json.loads(buf.getvalue())
        self.assertTrue(data["candidates"])
        self.assertEqual(data["candidates"][0]["component"]["type"], "text")

    def test_cli_jinja_matches_measure(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            cli.main(["--vendored", "jinja", "--font", "pix24", "--chars", "0123456789.°", "--var", "t"])
        out = buf.getvalue()
        self.assertIn('{".": 4, "0": 10, "1": 8, "°": 6}', out)  # checked in Home Assistant: 25.0° = 41 px
        self.assertIn("adv.get(c, 11)", out)
        self.assertIn("ns.w - 1", out)

    def test_cli_fonts_json(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            cli.main(["--vendored", "fonts", "--json"])
        self.assertEqual(len(json.loads(buf.getvalue())["fonts"]), 10)


if __name__ == "__main__":
    unittest.main()
