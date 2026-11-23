# news-image-20261122-wire

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/sarivenia84-netizen/news-image-20261122-wire/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/sarivenia84-netizen/news-image-20261122-wire/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

THE WIRE — a one-page visual summary of the world's news for Sunday, 22 November 2026: 18 date-checked stories across 9 regions, each with a headline, region tag and source attribution (Reuters, AP, CNN, Xinhua, NYT, WaPo, CNBC, Euronews), plus a COP31 lead-story banner and a DATE-CHECK strip. Rendered procedurally as a 1024x1024 PNG by a stdlib-only Python program (zlib + struct only): a hand-built 5x7 bitmap font, multi-column newspaper layout, and a PNG writer. Deterministic: two runs write identical bytes; no network, no external packages.

## Run it

```sh
python3 main.py
```

The image is written to ./entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png if set).

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>