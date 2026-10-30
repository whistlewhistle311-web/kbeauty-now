# K-Beauty Now work backlog

Every loop wake: do the checks, then take the top open item, finish it (build, check on a phone-width screenshot, push), tick it here with the date, and log one line in the ledger. Add new items when you find them. Highest expected traffic or money first.

## Open
RULE (2026-10-30): no new K-beauty pages. Work only on video format tests, measurement and fixes. Checkpoint 2026-11-13: if reel/TikTok average views < 300 and site visits < 50/day (Cloudflare Web Analytics), keep K-beauty on autopilot and stop adding work.
0c. Daily: record site page views/visits (Cloudflare Web Analytics, koreanbeautynow.com) in the ledger 현황 tab, row 'K-Beauty 사이트 방문'.
0b. Daily (first wake after 12:00 KST): record reel and TikTok views in the ledger 현황 tab (rows '인스타 릴스' and '틱톡': users=followers, impressions=views, posts=count, note=per-video views, avg watch time, skip rate, style a/b/routine). Judge the A/B on 11/6.
0. Weekly (Mondays): Amazon ASIN check for new top-10 entrants only (exact brand + product match, else keep the search link).
1. Product images: only via Amazon's own tools for Associates (PA-API needs 3 sales first) or brand-provided images; never hotlink Hwahae. Revisit after the first 3 sales.
2. Contact without exposing a personal email: Cloudflare Email Routing contact@koreanbeautynow.com → forward (needs MX records; DNS changes are 휘's click).
4. Ledger 현황 tab gets the same TOPIK/K-Beauty "자동 집계" rows appended every hour (writer not in this repo; likely an Apps Script or an external task on the sheet). Find it and make it update one row per day instead of appending, so the tab stays readable.
3. Pinterest username exposes 'whistlewhistle311': rename to koreanbeautynow (휘's account setting) and update links.

## Done
- 2026-10-30 Hub pages /guide/, /ingredient/, /concern/ got a real paragraph each (how to use, name-match caveat, reviews are not medical claims).
- 2026-10-30 Independent audit (subagent) → fixed: Amazon button on every card, affiliate note at top of every page, two-row mobile nav, home H1 "What Korean reviewers rate highest", "Korea store price", English sizes, Korean bracket notes dropped from names, acne claim reworded, privacy page, Apify promo removed from footer, track record hidden until 14 days, compare pairs + duplicate skin guides noindex (sitemap 76 → 48).
- 2026-10-30 Amazon ASIN audit against live Amazon titles: removed 14 links (shade-specific cushions/tints/gloss, packs of 2, TONYMOLY 'Milky' toner variant, S.NATURE pore moisturizer mismatch). Rule: no direct link for shade or multi-pack products; same product in a different size is OK.
- 2026-10-30 Hwahae rankings did not refresh on Fri 10/30 05:00 (last: Thu 10/29 05:00), so 'updated daily' was not true. Reworded sitewide to 'checked daily against Hwahae' and dropped '(Updated Daily)' from titles. If Hwahae turns out weekly (check Thu 11/5), say 'Hwahae updates weekly' outright. IG/TikTok/Pinterest bios still say 'daily' (bios: fix by hand later).
- 2026-10-30 Apify Store survey (public API): outside naver-shopping-scraper (2,132 users/30d, zen-studio) and naver-product-detail (2,054, delicious_zebu), every Korean niche has 0-70 users split across 3-6 near-identical actors (coupang 30-70 each, olive young 11-21, hwahae 2-9, musinsa/kream/bunjang/zigbang/jobs/books 0-7). kdatafactory and others already cover almost every site. Decision: no new actors; building more supply into a saturated, tiny market repeats the K-beauty mistake. Keep the 5 live + Danawa (publish 15:45) as they are.
- 2026-10-30 guide/seoul-shopping-list/ (each category's #1 and #2 with Korean names and prices, routine total ₩182,000) + home card. Threads nightly post rotates top 5 / value / #1 vs #2.
- 2026-10-30 og:image on compare/value pages uses the month's pin when rendered. Posting rotation table in the playbook. IndexNow already sends the whole sitemap (compare/ and value/ included).
- 2026-10-30 Pinterest feed rss-skin.xml connected to the board 'Korean Skincare by Skin Type'.
- 2026-10-30 r/dataisbeautiful: rules = [OC] tag, plain title, source + tool in first comment (no stated karma rule). Chart + post text drafted in ops/drafts/. Reddit is blocked for the browser extension, so a human has to post it; offer it to 휘, don't push.
- 2026-10-30 Workflows retry push after pull --rebase (daily-rankings failed once racing apify-sync).
- 2026-10-30 Video 'concern' (skin problem → Korea's pick). Skin-type pins get their own feed docs/rss-skin.xml for the board 'Korean Skincare by Skin Type'.
- 2026-10-30 Video 'hype': US favorites vs Korea's #1 (4 categories), first post tonight 22:37.
- 2026-10-30 Pinterest: profile and main board already keyword-rich; guides board description written (routine, sunscreen, value per 100 ml, comparisons, concerns, brands).
- 2026-10-30 Reddit: r/AsianBeauty requires 20 real comment karma, 1:10 self-promo ratio, 2 posts/week, OC flair, affiliate disclosure. We won't fake karma, so no post until the account honestly qualifies; the weekly draft now carries an operator + affiliate disclosure and these notes.
- 2026-10-30 Compare pins (#1 vs #2 per category, 8, monthly) on the guides board.
- 2026-10-30 Outlier research (vidIQ) + ops/reel_playbook.md (formats, hooks, hashtag sets); routine video style ("full routine of #1s costs $92 in Seoul").
- 2026-10-30 Searched Amazon US for the 35 top-10 products without an ASIN: none had an exact brand+product match (Korea-only items or different names), so they keep search links. Re-check new entrants weekly.
- 2026-10-30 Threads keyed by real KST date (stale Hwahae date made tonight's post skip); nightly post alternates with a value post.
- 2026-10-30 ItemList JSON-LD on value pages.
- 2026-10-30 Product pages link to the head-to-head pages they appear in.
- 2026-10-30 Compare pages (24) + compare hub + value pages (5); links from category pages and home.
- 2026-10-30 Korean price on reel slides; style b price-hook video; A/B by time of day.
- 2026-10-30 Pins picked by the real KST date; up to 2 evergreen pins a day; monthly value pins.
