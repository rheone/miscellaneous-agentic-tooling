import os
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.dirname(TOOLS)
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

from pixoo_kit import source  # noqa: E402

_SRC = None


def src():
    """The vendored 1.24.0 snapshot, so tests do not depend on what is installed."""
    global _SRC
    if _SRC is None:
        _SRC = source.load(vendored=True)
    return _SRC
