#!/usr/bin/env python3
"""Pixoo 64 font and layout tools (divoom_pixoo 1.24.0). Run: python -I pixoo.py -h"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pixoo_kit.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
