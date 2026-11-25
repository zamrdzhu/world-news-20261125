# world-news-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/zamrdzhu/world-news-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/zamrdzhu/world-news-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

**THE WORLD TODAY** — one 1024x1024 front page summing up Wednesday
25 November 2026's world news in 57 sourced stories: the CIA and ODNI
cyberattack, Huawei's guilty verdict in the US trial, Shenzhou-24 carrying
the first Pakistani astronaut to Tiangong, Zelenskiy's confirmation of the
Ukraine strike on a Russian ship, and the rest of the day across nine
sections — World, Middle East, Europe, Asia-Pacific, Africa, Americas,
Markets & Tech, Science & Space, and Sport.

Every headline is a real event of 25 November 2026 (or first reported that
day), gathered from Reuters, AP, BBC, Al Jazeera and CNN on the morning of
the 25th. The image is drawn by a stdlib-only Python program: a hand-rolled
5x7 bitmap font and a hand-written PNG encoder, no network, no randomness —
the same bytes on every run.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024x1024, under 1 MiB). Run it twice and the
two files are byte-identical (`sha256sum` to check).

## Layout

- Masthead: **THE WORLD TODAY**, Wednesday 25 November 2026, with a small
  drawn globe.
- Two lead stories, then 55 stories in nine colour-coded sections across
  three columns, then a sources footer.
- Headlines are kept short (at most two lines in a column) so the page
  stays legible; the renderer raises an error instead of overflowing the
  page if a story ever does not fit.

---

<sub>Entered on [make.fun](https://make.fun/?ref=ta9jpaag&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
