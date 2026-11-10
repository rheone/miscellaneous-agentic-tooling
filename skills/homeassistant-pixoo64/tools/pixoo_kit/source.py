"""Load the divoom_pixoo font code, from an installed integration or the vendored 1.24.0 copy.

The tools never re-implement the renderer. They import the integration's own
`pixoo64/_bdf.py` and `pixoo64/_font.py`, so every width, line height and pixel
comes from the code that draws on the device.

Resolution order (first hit wins):
  1. an explicit integration directory (`--integration`, or env PIXOO_INTEGRATION_DIR)
  2. an installed copy found by walking up from the working directory and from this file
     (`<dir>/custom_components/divoom_pixoo`), or `/config/custom_components/divoom_pixoo`
  3. the vendored snapshot in `vendor/divoom_pixoo` (integration 1.24.0)
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
import types
import warnings
from typing import List, Optional

BASED_ON = "1.24.0"
HERE = os.path.dirname(os.path.abspath(__file__))
VENDORED_DIR = os.path.join(HERE, "vendor", "divoom_pixoo")
_TRACKED = ("pixoo64/_bdf.py", "pixoo64/_font.py", "pixoo64/_colors.py")


def _is_integration(path: str) -> bool:
    return os.path.isfile(os.path.join(path, "pixoo64", "_bdf.py")) and os.path.isfile(
        os.path.join(path, "pixoo64", "_font.py"))


def find_installed(start_dirs: Optional[List[str]] = None) -> Optional[str]:
    """Return the first installed integration directory found, or None."""
    env = os.environ.get("PIXOO_INTEGRATION_DIR")
    if env and _is_integration(env):
        return os.path.abspath(env)
    for start in start_dirs or [os.getcwd(), HERE]:
        cur = os.path.abspath(start)
        while True:
            cand = os.path.join(cur, "custom_components", "divoom_pixoo")
            if _is_integration(cand):
                return cand
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
    if _is_integration("/config/custom_components/divoom_pixoo"):
        return "/config/custom_components/divoom_pixoo"
    return None


def _file_hash(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


class Source:
    """One loaded copy of the integration's font code plus a FontManager like the one HA builds."""

    def __init__(self, integration_dir: str, origin: str, config_dir: Optional[str] = None):
        self.integration_dir = os.path.abspath(integration_dir)
        self.origin = origin  # "installed", "explicit" or "vendored"
        self.config_dir = config_dir
        self.version = self._read_version()
        pkg_name = "_pixoo_src_" + hashlib.md5(self.integration_dir.encode()).hexdigest()[:10]
        if pkg_name not in sys.modules:
            pkg = types.ModuleType(pkg_name)
            pkg.__path__ = [os.path.join(self.integration_dir, "pixoo64")]  # no __init__ run: it needs PIL
            sys.modules[pkg_name] = pkg
        self.bdf = importlib.import_module(pkg_name + "._bdf")
        self.font_data = importlib.import_module(pkg_name + "._font")
        self.font_dirs = [os.path.join(self.integration_dir, "fonts")]
        if config_dir:
            # Same order as the integration's setup_font_manager(): later directories win.
            self.font_dirs += [os.path.join(config_dir, "fonts"), os.path.join(config_dir, "esphome", "fonts")]
        self.manager = self.new_manager()

    def new_manager(self):
        """A fresh FontManager (not the singleton), scanned like Home Assistant does at setup."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return self.bdf.FontManager([d for d in self.font_dirs if os.path.isdir(d)])

    def _read_version(self) -> str:
        try:
            with open(os.path.join(self.integration_dir, "manifest.json"), encoding="utf-8") as fh:
                return str(json.load(fh).get("version", "unknown"))
        except (OSError, ValueError):
            return "unknown"

    def drift(self) -> List[str]:
        """Differences between this copy and the vendored 1.24.0 snapshot (empty list = identical)."""
        notes = []
        if self.version != BASED_ON:
            notes.append(f"integration version {self.version}, skill written for {BASED_ON}")
        if self.origin != "vendored":
            for rel in _TRACKED:
                mine, ref = os.path.join(self.integration_dir, rel), os.path.join(VENDORED_DIR, rel)
                if os.path.isfile(mine) and _file_hash(mine) != _file_hash(ref):
                    notes.append(f"{rel} differs from the 1.24.0 snapshot")
        return notes

    def describe(self) -> str:
        where = f"{self.origin} {self.integration_dir}"
        extra = f"; user font dirs under {self.config_dir}" if self.config_dir else ""
        return f"divoom_pixoo {self.version} ({where}{extra})"


def load(integration_dir: Optional[str] = None, vendored: bool = False,
         config_dir: Optional[str] = None) -> Source:
    """Load font code. See the module docstring for the resolution order."""
    if vendored:
        return Source(VENDORED_DIR, "vendored", config_dir)
    if integration_dir:
        if not _is_integration(integration_dir):
            raise SystemExit(f"Not a divoom_pixoo integration directory: {integration_dir}")
        cfg = config_dir or os.path.dirname(os.path.dirname(os.path.abspath(integration_dir)))
        return Source(integration_dir, "explicit", cfg)
    found = find_installed()
    if found:
        cfg = config_dir or os.path.dirname(os.path.dirname(found))
        return Source(found, "installed", cfg)
    return Source(VENDORED_DIR, "vendored", config_dir)
