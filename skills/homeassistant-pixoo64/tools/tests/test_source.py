import os
import tempfile
import unittest

from _base import src
from pixoo_kit import source


class SourceTests(unittest.TestCase):
    def test_vendored_is_1_24_0_without_drift(self):
        s = src()
        self.assertEqual(s.version, "1.24.0")
        self.assertEqual(s.origin, "vendored")
        self.assertEqual(s.drift(), [])

    def test_env_var_points_at_integration(self):
        old = os.environ.get("PIXOO_INTEGRATION_DIR")
        os.environ["PIXOO_INTEGRATION_DIR"] = source.VENDORED_DIR
        try:
            self.assertEqual(os.path.normcase(source.find_installed([tempfile.gettempdir()])),
                             os.path.normcase(source.VENDORED_DIR))
        finally:
            if old is None:
                del os.environ["PIXOO_INTEGRATION_DIR"]
            else:
                os.environ["PIXOO_INTEGRATION_DIR"] = old

    def test_explicit_dir_must_be_an_integration(self):
        with self.assertRaises(SystemExit):
            source.load(integration_dir=tempfile.gettempdir())

    def test_user_font_dir_overrides_and_adds(self):
        with tempfile.TemporaryDirectory() as cfg:
            os.makedirs(os.path.join(cfg, "fonts"))
            bdf = os.path.join(source.VENDORED_DIR, "fonts", "Tiny5.bdf")
            with open(bdf, encoding="utf-8") as a, open(os.path.join(cfg, "fonts", "MyFont.bdf"), "w", encoding="utf-8") as b:
                b.write(a.read())
            s = source.load(vendored=True, config_dir=cfg)
            from pixoo_kit import fonts as F
            self.assertIn("myfont", F.font_keys(s))
            self.assertEqual(F.info(s, "myfont").origin, "user")


if __name__ == "__main__":
    unittest.main()
