"""Write a 64x64 preview PNG with the standard library only."""
from __future__ import annotations

import struct
import zlib
from typing import List, Tuple


def _chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write(path: str, pixels: List[List[Tuple[int, int, int]]], scale: int = 8, led: bool = True) -> None:
    """Save `pixels` (rows of RGB) scaled up. `led` draws each pixel as a dot with a dark gap, like the panel."""
    h, w = len(pixels), len(pixels[0])
    rows = []
    gap = 1 if led and scale >= 4 else 0
    for y in range(h * scale):
        row = bytearray([0])
        sy = y % scale
        for x in range(w * scale):
            sx = x % scale
            if gap and (sx >= scale - gap or sy >= scale - gap):
                row += bytes((12, 12, 12))
            else:
                r, g, b = pixels[y // scale][x // scale]
                row += bytes((r, g, b))
        rows.append(bytes(row))
    raw = zlib.compress(b"".join(rows), 9)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        fh.write(_chunk(b"IHDR", struct.pack(">IIBBBBB", w * scale, h * scale, 8, 2, 0, 0, 0)))
        fh.write(_chunk(b"IDAT", raw))
        fh.write(_chunk(b"IEND", b""))
