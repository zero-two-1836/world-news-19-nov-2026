[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/zero-two-1836/world-news-19-nov-2026/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/zero-two-1836/world-news-19-nov-2026/reward.svg)](https://make.fun/bounty/news-image-20261119)

# The World in One Picture — 19 November 2026

Entry for the make.fun bounty **"Sum up 19 November's world news in one
image"** ($250, ends Sat 21 Nov 2026 07:00 WIB).

## What it is

One image that sums up Thursday 19 November 2026: a newspaper front
page with **three illustrated lead stories, a 9-story grid, and a
numbers strip** — 12 stories from 6 continents, all legible at a glance.

- **Lead:** Gamers enter Vice City as GTA VI begins its global
  rollout after a 13-year wait.
- **Diplomacy:** Trump, Xi and Putin shake hands in Shenzhen at the
  APEC summit, ahead of a trilateral meeting with Ukraine on the
  agenda.
- **Markets:** Anthropic debuts at $83 in the biggest IPO ever —
  $81.3bn raised, valued at more than $1.4tn.
- **Plus:** Voyager 1 reaching one light-day out, the U.S. and Iran
  trading fire again across the Gulf, the EU's proposed €45bn Ukraine
  loan, another attack on the Crimean Bridge, Cyclone Akvan nearing
  India's coast, a Van Gogh selling for a record $190.4m, Myanmar's
  genocide verdict at the UN court, Hakeem Jeffries set to become the
  first Black Speaker of the U.S. House, and Finland approving the
  world's first nuclear waste repository.

## How to run

```sh
python3 main.py        # writes entry.png to /output
```

Requirements: Python 3.12+, standard library only, no network. The
program copies the bundled image (`assets/entry.png`, 1024×1024 PNG,
~127 KB) to `/output/entry.png`. Running it twice produces
byte-identical output. It checks the asset is a real PNG, under the
1 MiB limit, exactly 1024×1024, and verifies the written copy
byte-for-byte.

## How the poster is made

`build_image.py` renders `assets/entry.png` with Pillow (build-time
only): a serif masthead, a red kicker, three illustrated hero scenes
(a synthwave Vice City sunset, the three Shenzhen flags over a
skyline, and an IPO bar chart with a rising trend line), a 3×3 grid
with a hand-drawn pictogram per story, a gold-on-navy numbers strip
and a sources footer. All drawing code was written from scratch in
the build session; nothing is copied from any earlier build.

## Sources

BBC, Reuters, AP, Al Jazeera and NPR reporting of 19 November 2026.
See NEWS.md for the story list.
