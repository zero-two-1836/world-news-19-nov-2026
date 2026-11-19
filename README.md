[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/zero-two-1836/world-news-19-nov-2026/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/zero-two-1836/world-news-19-nov-2026/reward.svg)](https://make.fun/bounty/news-image-20261119)

# The World in One Picture — 19 November 2026

Entry for the make.fun bounty **"Sum up 19 November's world news in one
image"** ($250, ends Sat 21 Nov 2026 07:00 WIB).

## What it is

One image that sums up Thursday 19 November 2026: a poster with
**three illustrated lead stories, an 8-story grid, and a numbers
strip** — 12 stories from 6 continents.

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
  genocide verdict at the UN court, and Hakeem Jeffries set to become
  the first Black Speaker of the U.S. House.

## How to run

```sh
python3 main.py        # writes entry.png to /output (or ./output)
```

Requirements: Python 3.13, standard library only, no network. The program
copies the bundled image (`assets/entry.png`, 1024×1024 PNG, ~122 KB) to
`/output/entry.png`. Running it twice produces byte-identical output.

## How the image was made

`build_image.py` renders the poster with Pillow from the verified
story list in `NEWS.md`. The judge reads images at a glance, so the
poster uses large flat illustrations and one-line headlines instead of
dense body copy, and stays legible at ~300 pixels across. It is kept
in the repo so the image is fully reproducible; the submitted program
itself (`main.py`) needs no third-party packages.

## Sources

See `NEWS.md`. Headlines were verified on 19 Nov 2026 against BBC,
Reuters/AP wires, Al Jazeera, NPR and One Turn News summaries of
19 November 2026.

## License

MIT — see `LICENSE`.
