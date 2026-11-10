"""Golden facts for divoom_pixoo 1.24.0. A failure after an integration update means the skill text needs review."""
import unittest

from _base import src
from pixoo_kit import fonts as F


class CatalogTests(unittest.TestCase):
    def test_font_names(self):
        self.assertEqual(F.font_keys(src()), ["clock", "eleven_pix", "five_pix", "gicko", "pico_8", "pix24",
                                              "pixelifysans", "pressstart2p", "tiny5", "tiny5duo"])

    def test_line_heights_and_capitals(self):
        expect = {"pico_8": (6, 5), "gicko": (7, 6), "five_pix": (6, 5), "eleven_pix": (12, 11), "clock": (13, 12),
                  "pix24": (25, 24), "tiny5": (9, 5), "tiny5duo": (9, 5), "pressstart2p": (8, 7), "pixelifysans": (13, 7)}
        for key, (lh, cap) in expect.items():
            i = F.info(src(), key)
            self.assertEqual((i.line_height, i.cap_height), (lh, cap), key)
            self.assertEqual(i.cap_top, 0, key)

    def test_pico_8_is_the_bdf_with_small_caps(self):
        i = F.info(src(), "pico_8")
        self.assertEqual(i.kind, "bdf")
        self.assertEqual(i.lowercase, "small-caps")
        self.assertTrue(i.monospace)
        self.assertEqual(i.per_line["0"], 16)
        self.assertEqual(F.resolve(src(), "FONT_PICO_8")[0].name, "PICO_8")

    def test_lower_case_kinds(self):
        kinds = {k: F.info(src(), k).lowercase for k in ("gicko", "eleven_pix", "five_pix", "clock", "tiny5")}
        self.assertEqual(kinds, {"gicko": "upper-case fallback", "eleven_pix": "upper-case fallback",
                                 "five_pix": "same as capitals", "clock": "none (no letters)", "tiny5": "true"})

    def test_ink_above_y(self):
        self.assertEqual(F.info(src(), "tiny5").ink_top_ascii, -1)
        self.assertEqual(F.info(src(), "pixelifysans").ink_top_any, -4)
        self.assertEqual(F.info(src(), "gicko").ink_top_ascii, 0)

    def test_press_start_lines_touch(self):
        notes = " ".join(F.info(src(), "pressstart2p").notes)
        self.assertIn("no blank row", notes)

    def test_tabular_digits(self):
        tab = {k: F.info(src(), k).tabular_digits for k in ("pico_8", "tiny5", "eleven_pix", "pix24", "gicko", "pixelifysans")}
        self.assertEqual(tab, {"pico_8": True, "tiny5": True, "eleven_pix": True, "pix24": False, "gicko": False,
                               "pixelifysans": False})


class GlyphTests(unittest.TestCase):
    def g(self, font, ch):
        return F.glyph(src(), F.get(src(), font), ch)

    def test_blank_glyphs_in_pico_8(self):
        self.assertEqual(self.g("pico_8", "É").status, F.BLANK)
        self.assertEqual(self.g("pico_8", "é").status, F.BLANK)  # falls back to the blank capital

    def test_missing_in_big_fonts(self):
        for font, ch in (("eleven_pix", "%"), ("eleven_pix", "-"), ("eleven_pix", "+"), ("pix24", "-"),
                         ("pix24", "!"), ("clock", "A")):
            self.assertEqual(self.g(font, ch).status, F.MISSING, (font, ch))

    def test_missing_matrix_glyph_draws_nothing_but_counts_a_pixel(self):
        g = self.g("eleven_pix", "%")
        self.assertEqual((g.advance, g.width_counted, g.ink), (0, 1, None))

    def test_missing_bdf_glyph_draws_question_mark(self):
        g = self.g("pico_8", "€")
        self.assertEqual((g.status, g.drawn_as), (F.MISSING, "?"))
        self.assertIsNotNone(g.ink)

    def test_typography_fallback_single_char_only(self):
        self.assertEqual(self.g("gicko", "—").status, F.TYPO)
        self.assertEqual(self.g("five_pix", "→").status, F.MISSING)  # '->' is two characters: never used

    def test_case_fallback(self):
        g = self.g("gicko", "a")
        self.assertEqual((g.status, g.drawn_as), (F.CASE, "A"))

    def test_degree_coverage(self):
        for font in ("pico_8", "gicko", "five_pix", "eleven_pix", "pix24", "tiny5", "pressstart2p", "pixelifysans"):
            self.assertEqual(self.g(font, "°").status, F.OK, font)
        self.assertEqual(self.g("clock", "°").status, F.MISSING)


if __name__ == "__main__":
    unittest.main()
