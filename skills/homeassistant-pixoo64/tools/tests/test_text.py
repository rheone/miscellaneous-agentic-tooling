import unittest

from _base import src
from pixoo_kit import text as T


class MeasureTests(unittest.TestCase):
    def test_overflow_is_reported(self):
        m = T.measure(src(), "five_pix", "WET LOAD WAITING", 32, 30, "center")
        self.assertEqual(m.lines[0].width, 76)
        self.assertGreater(m.off_canvas, 0)
        self.assertFalse(m.fits)

    def test_centre_start_uses_floor_of_half_width(self):
        m = T.measure(src(), "pico_8", "ABC", 32, 0, "center")  # width 12 -> start 26
        self.assertEqual(m.lines[0].start_x, 26)

    def test_right_align_gap_hint_for_bdf(self):
        m = T.measure(src(), "pico_8", "88", 63, 0, "right")
        self.assertEqual(m.ink[2], 61)
        self.assertTrue(any("x=65" in h for h in m.hints))

    def test_matrix_right_align_ends_at_x_minus_1(self):
        m = T.measure(src(), "gicko", "88", 63, 0, "right")
        self.assertEqual(m.ink[2], 62)

    def test_unknown_font_falls_back(self):
        m = T.measure(src(), "comic_sans", "Hi", 32, 0, "center")
        self.assertTrue(m.fell_back)
        self.assertEqual(m.font, "pico_8")

    def test_invalid_align_is_left(self):
        m = T.measure(src(), "pico_8", "Hi", 10, 0, "centre")
        self.assertEqual(m.lines[0].start_x, 10)
        self.assertTrue(any("left-aligned" in s for s in m.issues))

    def test_ink_above_y_is_reported(self):
        m = T.measure(src(), "tiny5", "ice", 32, 0, "center")
        self.assertEqual(m.ink[1], -1)
        self.assertGreater(m.off_canvas, 0)

    def test_lower_case_is_not_uppercased_in_bdf(self):
        upper = T.measure(src(), "tiny5", "ABC", 0, 0, "left")
        lower = T.measure(src(), "tiny5", "abc", 0, 0, "left")
        self.assertNotEqual(set(upper.pixels), set(lower.pixels))


class WrapTests(unittest.TestCase):
    def test_fewest_lines_then_balanced(self):
        lines = T.wrap(src(), "gicko", "AWAY MISSION COMPLETE", 62)
        self.assertEqual(lines, ["AWAY", "MISSION", "COMPLETE"])

    def test_word_too_long(self):
        self.assertIsNone(T.wrap(src(), "gicko", "AUTHENTICATED", 62))

    def test_hyphenate(self):
        lines = T.wrap(src(), "gicko", "AUTHENTICATED", 62, hyphenate=True)
        self.assertTrue(lines[0].endswith("-"))
        self.assertEqual("".join(l.rstrip("-") for l in lines), "AUTHENTICATED")

    def test_max_lines(self):
        self.assertIsNone(T.wrap(src(), "gicko", "AWAY MISSION COMPLETE", 62, max_lines=2))

    def test_keep_breaks(self):
        self.assertEqual(T.wrap(src(), "pico_8", "A B\nC", 62, keep_breaks=True), ["A B", "C"])


class SuggestTests(unittest.TestCase):
    def test_value_prefers_big_tabular_font(self):
        cands, rejected, role = T.suggest(src(), "72.5°F", (0, 14, 64, 26), role="value", stable=True)
        self.assertEqual(role, "value")
        self.assertEqual(cands[0].font, "eleven_pix")
        pix24 = [r for r in rejected if r.font == "pix24"][0]
        self.assertIn("second, smaller component", pix24.reason)

    def test_every_candidate_fits_its_box(self):
        box = (0, 20, 64, 24)
        cands, _, _ = T.suggest(src(), "Garage door open", box)
        self.assertTrue(cands)
        for c in cands:
            x0, y0, x1, y1 = c.ink
            self.assertGreaterEqual(x0, box[0] + 1)
            self.assertLessEqual(x1, box[0] + box[2] - 2)
            self.assertGreaterEqual(y0, box[1])
            self.assertLessEqual(y1, box[1] + box[3] - 1)
            m = T.measure(src(), c.font, "\n".join(c.lines), c.position[0], c.position[1], c.align)
            self.assertEqual(m.ink, c.ink)

    def test_keep_case_rejects_capital_fallback(self):
        cands, rejected, _ = T.suggest(src(), "Hello", keep_case=True)
        self.assertNotIn("gicko", [c.font for c in cands])
        self.assertIn("gicko", [r.font for r in rejected])
        self.assertIn("five_pix", [r.font for r in rejected])  # its lower case copies the capitals (seen on the device)

    def test_role_guess(self):
        self.assertEqual(T.guess_role("12:45"), "time")
        self.assertEqual(T.guess_role("72°F"), "value")
        self.assertEqual(T.guess_role("Door open"), "headline")
        self.assertEqual(T.guess_role("The washing machine has finished"), "body")


class BudgetTests(unittest.TestCase):
    def test_budget(self):
        b = T.budget(src(), "pico_8", 62)
        self.assertEqual(b["digits"]["worst_case"], 15)
        self.assertIsNone(T.budget(src(), "clock", 62)["upper"])

    def test_strip_templates(self):
        static, n, logic = T.strip_templates("T {{ states('x') }}°")
        self.assertEqual((static, n, logic), ("T °", 1, False))


if __name__ == "__main__":
    unittest.main()
