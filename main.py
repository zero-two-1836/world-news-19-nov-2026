#!/usr/bin/env python3
"""Sum up 19 November's world news in one image.

Entry for the make.fun bounty "Sum up 19 November's world news in one
image" ($250). The program writes one image, /output/entry.png:
a poster summarising Thursday 19 November 2026 —
12 stories from 6 continents, plus a numbers strip.

Design: the image itself is a fixed asset (assets/entry.png) rendered
when the repository was built from verified reporting of 19 Nov 2026
(see NEWS.md and build_image.py). This program is deliberately tiny,
stdlib-only and fully deterministic: it copies those exact bytes to
/output/entry.png, so two runs always produce identical output.

Stdlib only. No network. No randomness. No clock reads.
"""
import hashlib
from pathlib import Path

ASSET = Path(__file__).resolve().parent / "assets" / "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def output_path() -> Path:
    """The bounty sandbox provides /output; fall back to ./output."""
    for candidate in (Path("/output"), Path(__file__).resolve().parent / "output"):
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".write-test"
            probe.write_bytes(b"")
            probe.unlink()
            return candidate / "entry.png"
        except OSError:
            continue
    raise OSError("no writable output directory found")


def main() -> None:
    data = ASSET.read_bytes()
    if not data.startswith(PNG_MAGIC):
        raise ValueError("assets/entry.png is not a valid PNG")
    if len(data) > 1_048_576:
        raise ValueError("assets/entry.png exceeds the 1 MiB limit")
    dest = output_path()
    dest.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    print(f"wrote {dest} ({len(data)} bytes, sha256 {digest})")


if __name__ == "__main__":
    main()
