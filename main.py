#!/usr/bin/env python3
"""Copy the bundled poster to the grading output directory.

Entry point for the make.fun bounty "Sum up 19 November's world
news in one image". The poster is a fixed asset (assets/entry.png)
rendered at build time from verified reporting of 19 Nov 2026
(see NEWS.md and build_image.py). This program is deliberately tiny
and deterministic: it checks the asset, then copies its exact bytes
to /output/entry.png, so two runs always produce identical output.

Standard library only. No network. No randomness. No clock reads.
"""

import hashlib
import struct
from pathlib import Path

ASSET = Path(__file__).resolve().parent / "assets" / "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
WANT_W, WANT_H = 1024, 1024


def load_asset():
    """Read and validate the bundled poster; return its bytes."""
    data = ASSET.read_bytes()
    if not data.startswith(PNG_MAGIC):
        raise ValueError("assets/entry.png is not a valid PNG")
    if len(data) > MAX_BYTES:
        raise ValueError("assets/entry.png exceeds the 1 MiB limit")
    # IHDR starts at byte 16: width and height, big-endian uint32.
    # The bounty wants a 1024x1024 image, so refuse a wrong-sized asset
    # instead of silently shipping it.
    w, h = struct.unpack(">II", data[16:24])
    if (w, h) != (WANT_W, WANT_H):
        raise ValueError(
            f"assets/entry.png is {w}x{h}, expected "
            f"{WANT_W}x{WANT_H}")
    return data


def output_path():
    """Pick the grading output dir, falling back to ./output."""
    for candidate in (Path("/output"),
                      Path(__file__).resolve().parent / "output"):
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".write-test"
            probe.write_bytes(b"")
            probe.unlink()
            return candidate / "entry.png"
        except OSError:
            continue
    raise OSError("no writable output directory found")


def main():
    data = load_asset()
    dest = output_path()
    dest.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    print(f"wrote {dest} ({len(data)} bytes, sha256 {digest})")


if __name__ == "__main__":
    main()
