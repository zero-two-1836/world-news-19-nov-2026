# Build transcript — "Sum up 19 November's world news in one image"

Rebuilt 19 Nov 2026 by a Muse agent for make.fun account @zero-two,
GitHub user zero-two-1836. Times are Asia/Jakarta (WIB, UTC+7). This
file is a hand-written, chronological record of the rebuild session,
made at build time.

## Why a rebuild (round 3)

Round 2 (submission 01a1f29f, "Civil Zenith") passed the server's
validity checks and ranked 1235/5287 — but its poster was built with
a minimal stdlib-only renderer (a 5×7 pixel typeface, flat colours),
which is visibly basic next to the top entries. The user ordered the
rank chased toward the top 10 and never below 500, so this round
rebuilds the poster to be richer and more polished: real
anti-aliased typography, gradient skies, detailed hero scenes and a
full 3×3 story grid, while keeping every line of code written fresh
in this session.

## Session log

- **15:20 WIB — brief received.** Improve the news-19 entry toward
  the top 10. Same 12 stories from NEWS.md. Build a richer
  1024×1024 poster, write all code from scratch in this session
  (never copy, re-type or move in code from the news-17 build or the
  earlier 19 Nov builds), revise each code file, verify, commit
  locally. Do not bundle or submit — the parent re-bundles and
  submits.
- **15:21 WIB — tools.** Pillow 10.2.0 is installed on this VM with
  DejaVu and Liberation TrueType fonts, so the poster can use real
  typography instead of a pixel font. PIL is build-time only;
  main.py stays stdlib-only.
- **15:22 WIB — build_image.py, written from scratch.** Wrote the
  renderer (about 16 KB) with Pillow: a serif masthead with a gold
  dateline, a red kicker, three illustrated hero scenes (a synthwave
  Vice City sunset with a slit sun and lit windows, the three
  Shenzhen flags over a windowed skyline with a gold handshake
  badge, and an IPO panel with a big gold $83 plus rising bars and
  a trend arrow), a 3×3 grid with a hand-drawn pictogram per story
  (star, drop, euro, bridge, waves, brush, scales, dome, atom), a
  gold-on-navy numbers strip and a sources footer. All 12 stories
  are present; Finland gets its own grid cell this time.
- **15:23 WIB — main.py, written from scratch.** Stdlib-only
  entrypoint: validates the PNG magic, the 1 MiB limit and the
  exact 1024×1024 IHDR dimensions, copies assets/entry.png to
  /output/entry.png and prints its sha256.
- **15:24 WIB — first render.** The poster rendered at 1024×1024
  (126,065 bytes) and main.py ran twice byte-identical, but the
  build failed first on a float passed to range() in the Shenzhen
  flag code. Fixed by casting the pole positions to int (edit 1).
- **15:25 WIB — visual check.** The poster looked good but had
  three defects: the atom icon read as an eye, the Vice City sun
  was half-hidden behind the skyline, and ~90 px of empty paper sat
  below the footer. Fixed in one revision round (edits 2–6): the
  atom became two crossed orbital ellipses with a nucleus, the sun
  was raised clear of the skyline, the palms were moved inside the
  frame, and the layout was stretched (taller hero cards, taller
  grid rows, numbers strip and footer moved down) to fill the page.
- **15:26 WIB — main.py revision.** Added a read-back check: after
  writing /output/entry.png it is read again and compared
  byte-for-byte with the asset (edit 1 for main.py).
- **15:27 WIB — final verification.** Re-rendered: 1024×1024 RGB,
  126,661 bytes. Viewed at full size and as a 300 px downscale —
  all 12 stories present, masthead, heroes, grid and numbers strip
  legible at a glance. main.py run twice, byte-identical output.

## Files

- `build_image.py` — the Pillow renderer (this session's own code).
- `main.py` — stdlib-only entrypoint, copies the poster to /output.
- `assets/entry.png` — the finished 1024×1024 poster.
- `NEWS.md` — the 12 verified stories of 19 Nov 2026.
- `README.md` — entry description and run instructions.
