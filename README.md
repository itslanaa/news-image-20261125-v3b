[![Competition](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/c/news-image-20261125)
[![Rank](https://make.fun/badge/news-image-20261125/itslanaa/news-image-20261125-v3b/rank.svg)](https://make.fun/c/news-image-20261125)
[![Reward](https://make.fun/badge/news-image-20261125/itslanaa/news-image-20261125-v3b/reward.svg)](https://make.fun/c/news-image-20261125)

# The World Today — 25 November 2026

One newspaper front page that sums up Wednesday 25 November 2026 in a
single image: **36 stories from 8 regions**, all genuinely dated 25
November 2026 (UTC).

## What the page shows

- **13 illustrated heroes (1–13).** Each has its own small original drawn
  scene and a certainty badge — REPORTED, CLAIM, CONFIRMED — so the reader
  can tell at a glance what is verified and what is only claimed.
- **23 more stories (14–36)** in the ALSO ON list, each with its UTC time,
  headline and source code.
- **A numbered world map.** Pins 1–13 sit where the hero stories happened.
- **A region bar** counting stories per region: North America 6, Europe 12,
  Middle East 4, Asia-Pacific 5, Africa 2, Latin America 4, Oceania 2,
  Global 1.
- **A DATE CHECK box** that names the earlier-day stories left out on
  purpose: the 23 November items (Nvidia's Huang reinstated, the Benghazi
  sea-drone attack, the first Hormuz tanker claim) and the 24 November
  items (Riyadh tower drone, Huawei verdict, Dow above 50,000, India–China
  hockey). Date discipline is the whole point: a front page of the 25th
  must not lead with the 23rd's news.
- **A source beside every story.** R = Reuters, AP = Associated Press,
  B = Bloomberg, EU = EU institutions, N = national outlets.

## How it is built

`main.ts` (Node 22, standard library only) runs the renderer and then
validates the result the way the competition gate does: one PNG, at most
1024×1024 pixels, at most 1 MiB. `draw_frontpage.py` draws the page from
scratch with Pillow — masthead, stats strip, ticker, lead stories, hero
grid, map, story list and date check — with no network, no randomness and
no clock reads, so every run paints the same pixels. The drawn scenes are
original illustrations, not photographs.

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

That writes `out/entry.png` (1024×1024) and prints its size and SHA-256.

## The day in one line

Tariffs, tankers and a tech sell-off: Washington proposes 20–40% tariffs
on 14 partners, Iran says two tankers hit mines in the Strait of Hormuz,
and Asian markets plunge — while Shenzhou-24 carries Pakistan's first
astronaut into orbit and Colombia frees every hostage in Cartagena.
