#!/usr/bin/env python3
"""Copy the bundled poster to the grading output directory.

Entrypoint for the make.fun bounty "Sum up 19 November's world
news in one image". The poster is a fixed asset (assets/entry.png)
rendered at build time from verified reporting of 19 Nov 2026
(see NEWS.md and build_image.py). The program is deliberately tiny
and deterministic: it validates the asset, copies its exact bytes
to /output/entry.png, then reads the copy back to prove the two
files are byte-identical. Two runs always produce identical output.

Standard library only. No network. No randomness. No clock reads.
"""
import hashlib
import struct
import sys
from pathlib import Path

ASSET = Path(__file__).resolve().parent / "assets" / "entry.png"
OUTPUT = Path("/output") / "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
WANT_W, WANT_H = 1024, 1024
STORIES = 12


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
    try:
        data = ASSET.read_bytes()
    except FileNotFoundError:
        raise ValueError(
            "assets/entry.png is missing — run build_image.py first")
    if len(data) > MAX_BYTES:
        raise ValueError("assets/entry.png exceeds the 1 MiB limit")
    w, h = png_size(data)
    if (w, h) != (WANT_W, WANT_H):
        raise ValueError(
            "assets/entry.png is %dx%d, want %dx%d"
            % (w, h, WANT_W, WANT_H))
    return data


def write_output(data):
    """Write the asset to /output/entry.png and verify the copy."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(data)
    written = OUTPUT.read_bytes()
    if written != data:
        raise ValueError("/output/entry.png does not match assets/entry.png")
    return written


def main():
    data = load_asset()
    write_output(data)
    digest = hashlib.sha256(data).hexdigest()
    print("entry.png %d bytes %dx%d sha256=%s stories=%d -> %s"
          % (len(data), WANT_W, WANT_H, digest, STORIES, OUTPUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
