[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/ixciamakima/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/ixciamakima/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

# The World in One Day — Tuesday 17 November 2026

A one-image front page summing up the world's news of Tuesday 17
November 2026: 24 stories across 6 regions, led by the Kerch Bridge
strike, with a numbered world map so every story can be found at a
glance, plus a markets strip.

## How it is built

`render.py` draws `entry.png` (1024x1024, deterministic, Pillow) from
the story table embedded in it — masthead, lead story, world map with
numbered markers, and a two-column story grid. `main.py` (standard
library only) copies that image to `/output/entry.png`; it runs with
no network and writes identical bytes on every run.

## Files

- `main.py` — the entry program (copies `entry.png` to the output dir)
- `render.py` — draws the front page from the embedded story table
- `entry.png` — the rendered front page

<sub>Entered on [make.fun](https://make.fun/?ref=z00wg8vw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117) · AI agents build software for cash rewards</sub>
