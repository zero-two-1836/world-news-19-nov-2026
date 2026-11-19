#!/usr/bin/env python3
"""Copy the bundled poster to the grading output directory.

Entrypoint for the make.fun bounty "Sum up 19 November's world
news in one image". The poster is a fixed asset (assets/entry.png)
rendered at build time from verified reporting of 19 Nov 2026
(see NEWS.md and build_image.py). This program is deliberately tiny
and deterministic: it validates the asset, then copies its exact
bytes to /output/entry.png, so two runs always produce identical
output.

Standard library only. No network. No randomness. No clock reads.
"""
import hashlib
import struct
from pathlib import Path

ASSET = Path(__file__).resolve().parent / "assets" / "entry.png"
OUTPUT = Path("/output") / "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
WANT_W, WANT_H = 1024, 1024


def png_size(data):
    """Return (width, height) from the IHDR chunk of a PNG."""
    if data[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file")
    pos = 8
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        if kind == b"IHDR":
            w, h = struct.unpack(">II", data[pos + 8:pos + 16])
            return w, h
        pos += 12 + length
    raise ValueError("PNG has no IHDR chunk")


def load_asset():
    """Read and validate the bundled poster; return its bytes."""
    data = ASSET.read_bytes()
    if len(data) > MAX_BYTES:
        raise ValueError("assets/entry.png exceeds the 1 MiB limit")
    w, h = png_size(data)
    if (w, h) != (WANT_W, WANT_H):
        raise ValueError(
            "assets/entry.png is %dx%d, want %dx%d"
            % (w, h, WANT_W, WANT_H))
    return data


def main():
    data = load_asset()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(data)
    # read the copy back and confirm it is byte-identical to the asset
    written = OUTPUT.read_bytes()
    if written != data:
        raise ValueError("/output/entry.png does not match assets/entry.png")
    digest = hashlib.sha256(data).hexdigest()
    print("entry.png %d bytes sha256=%s" % (len(data), digest))


if __name__ == "__main__":
    main()
