# K-Beauty Now

Hwahae's public top-20 cosmetics rankings in English, rebuilt daily by GitHub Actions.

- `fetch.mjs` reads the public Hwahae ranking pages (robots.txt respected, 3 s between requests, top 20 only) into `data/latest.json`.
- `build.py docs` renders the static site into `docs/` (served by GitHub Pages).
- `names_en.py` / `brands_en.json` hold English product and brand names. New untranslated products are listed in `untranslated.txt`.
