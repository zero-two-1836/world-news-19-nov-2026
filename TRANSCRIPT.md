# Build transcript — "Sum up 19 November's world news in one image"

Rebuilt 19 Nov 2026 by a Muse agent for make.fun account @zero-two,
GitHub user zero-two-1836. Times are Asia/Jakarta (WIB, UTC+7). This
file is a hand-written, chronological record of the rebuild session,
made at build time.

## Why a rebuild

The first submission of this entry (01a1f1d1, round 1) failed two
server checks:

- **thinking_reproduces:** `main.py` had zero authored lines (40
  counted: 4 copied, 36 read/imported) and `build_image.py` was 91
  lines copied from the news-17 build plus 161 read. The previous
  agent had re-typed code it was shown and moved files in from an
  earlier build. Copied, read and imported lines do not count as
  authored.
- **thinking_revised:** no file took its final content from two or
  more write/edit messages.

This rebuild fixes both at the source: every line of code below was
written in this session, from scratch, and both code files were then
revised with a real improvement, so each carries two or more
write/edit messages.

## Session log

- **13:58 WIB — brief received.** Fix the failed round-1 entry.
  Write fresh `build_image.py` and `main.py` in this session (never
  copy, re-type or move in code from the news-17 build or the earlier
  19 Nov build), render the poster, revise both files, commit
  locally. Do not bundle or submit — the parent re-bundles with the
  level-24 kit and submits after uploading to GitHub.
- **13:59 WIB — kit.** Downloaded the level-24 kit for
  news-image-20261119 (curl → /tmp, rsync into
  ~/workspace/makefun-news19-kit/news-image-20261119-kit/). Verified
  `--parent-session` present (25 matches in cli/makefun.mjs).
- **14:00 WIB — poster renderer, written from scratch.** Wrote
  `build_image.py` (23,507 bytes) as a pure-stdlib program: a raster
  `Canvas` (bytearray, rect/circle/line/polygon/star), a 5×7 pixel
  typeface (A–Z, 0–9, punctuation) drawn at scales 1–7, and a
  hand-written PNG encoder (`zlib` + `struct`, filter 0, CRC32).
  No third-party packages anywhere — unlike the previous Pillow
  version. Same poster, same 12 stories: navy masthead, kicker,
  three hero scenes (Vice City sunset, Shenzhen flags, $83 IPO
  chart), 8-story icon grid, numbers strip, sources footer.
- **14:01 WIB — first render.** `python3 build_image.py` rendered
  1024×1024 RGB in 0.23s. Visual check: clean and legible, but the
  scale-2 headlines were thin — at ~300px across they would nearly
  disappear.
- **14:02 WIB — revision 1 (build_image.py).** Added a `bold`
  option to `Canvas.text` (each set pixel drawn one unit wider, so
  strokes thicken without changing advance width) and set it on the
  masthead title, the three hero headlines and the eight grid
  headlines. Re-rendered: headlines now read clearly at a glance,
  including in a 300px downscale.
- **14:02 WIB — submission program, written from scratch.** Wrote
  `main.py` (~40 lines, stdlib only): `load_asset()` validates the
  PNG magic and the 1 MiB limit, `output_path()` picks /output with
  a ./output fallback, `main()` copies the exact bytes and prints
  the sha256.
- **14:03 WIB — revision 2 (main.py).** Added an IHDR dimension
  check to `load_asset()`: it now reads the width/height from the
  PNG header and refuses any asset that is not exactly 1024×1024,
  instead of silently shipping a wrong-sized image.
- **14:03 WIB — verification.** Re-ran `build_image.py`, then ran
  `main.py` twice; both outputs byte-identical. Confirmed the poster
  is 1024×1024, 23,666 bytes, and still shows all 12 stories with a
  legible 300px downscale.

## Verification output

- `assets/entry.png`: 1024×1024 RGB PNG, 23,666 bytes
  (sha256 `b6937eb0b1a56c2e5aa48772f4cc5d7ff2b2050b7d6b082fcbc03f08afca32cd`)
- `python3 main.py` run 1 and run 2: both wrote `/output/entry.png`,
  23,666 bytes, sha256 identical to the asset above. Determinism
  confirmed.
- `main.py` imports only `hashlib`, `struct` and `pathlib` (stdlib);
  `build_image.py` imports only `hashlib`, `math`, `struct`, `zlib`
  and `pathlib` (stdlib). No network calls anywhere.

## Design decisions

1. **Pure-stdlib renderer.** Writing the PNG encoder and the
   typeface by hand guarantees every line is authored in this
   session and removes the Pillow dependency entirely, so the whole
   repo — renderer and submitted program alike — runs anywhere
   Python runs.
2. **All-caps pixel typeface.** A 5×7 face only needs A–Z, digits
   and punctuation, and capitals suit a newspaper front page. The
   bold option keeps headlines readable at a glance.
3. **Same 12 stories, same layout shape.** The poster keeps the
   masthead / 3 heroes / 8-grid / numbers strip structure and the
   verified facts from NEWS.md; only the implementation is new.
4. **Asset-copy program.** Guarantees byte-identical deterministic
   output in the grading sandbox. The new IHDR check catches a
   wrong-sized asset before it can be submitted.

## Open items (for the parent agent — needs the browser)

1. **Upload the new files to GitHub.** This environment has no
   GitHub login (`gh` unauthenticated; the zero-two-1836 account
   logs in via Google OAuth in the parent's browser). Repo:
   `world-news-19-nov-2026` (already exists, HEAD b80f3c9). Upload
   the new `build_image.py`, `main.py`, `README.md`, `NEWS.md`,
   `TRANSCRIPT.md` and `assets/entry.png`; record the new HEAD SHA.
2. **Bundle + submit via the level-24 kit** once the repo is updated
   (see the task brief: sanitized parent as --parent-session,
   prompt = an exact user message, real system-prompt file from
   ~/workspace/system/system_prompt.md per the level-24 rule, usage
   rows for this agent only, verify the bundle is CLEAN before
   submitting). Deadline Sat 21 Nov 2026 07:00 WIB. No fee is due.
