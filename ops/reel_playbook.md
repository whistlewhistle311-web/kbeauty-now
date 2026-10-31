# Reels / TikTok playbook

Read this before every reel or TikTok post.

## Formats (ops/shorts.mjs)
- `node ops/shorts.mjs <slug> <outdir>`: KST morning runs default to style b (price hook title), night runs to style a (countdown title). A/B judged on 11/6 by average watch time.
- 10/31 owner insights: 3 reels, 60 plays, skip rate 66-100%, avg watch 0.8-1.7s. Changed the first frame to a dark hook card with the number in pink and cut the title to 1.4s (from the 10/31 night reel on). Compare skip rate on 11/6: beige card (10/29-10/31 morning) vs dark card.
- `node ops/shorts.mjs routine <outdir>`: full 5-step routine from each step's #1 with the Seoul total ("A full Korean skincare routine costs $92 in Seoul"). Strongest hook we have; use it at least twice a week.

- `node ops/shorts.mjs hype <outdir>`: "What America buys vs what's #1 in Korea" (US favorites from ops/us_favorites.json against today's Hwahae ranks; e.g. Beauty of Joseon Relief Sun is #19 in Korea, COSRX Snail Mucin and Anua Heartleaf 77 are not in the top 20). Only state ranks the data shows; never say the US pick is bad. Hashtags: #kbeauty #koreanskincare #hwahae #skincareroutine #cosrx #beautyofjoseon #anua.
- `node ops/shorts.mjs concern <outdir>`: "Your skin problem → what Koreans actually use" (6 concerns: dehydrated, redness, breakouts, pores, sticky finish, sensitive; the best-ranked product Korean reviewers praise most for each). Hashtags: #kbeauty #koreanskincare #hwahae #skincareroutine #sensitiveskin #acne #skinbarrier.

## Posting rotation (KST)
- Night 22:37 (US morning): category countdown, style a, next category in order sunscreen → toner → serum → cream → cleansing → masks → cushion → lip → all. Saturday night: hype.
- Morning 09:37 (US evening): Mon category style b · Tue hype · Wed concern · Thu category style b · Fri routine · Sat concern · Sun routine.
- Same video goes to TikTok right after (휘 presses publish). Check the last 4 captions so the same category/format doesn't repeat back to back.
- 2026-10-30 night: hype (first run). 2026-10-31 (Sat) morning: routine (first run, overrides the table).

## What works for small accounts (vidIQ outlier search, 2026-10-30, Oct posts, under 50K followers)
- 600K to 13M views on 2K to 40K follower accounts came from: "Koreans have been gatekeeping", "what is actually #1 in Korea" vs what is hyped in the US, "concern → ingredient/product" quick maps, "products worth your $$" listicles.
- Fast pacing, music only, text overlays, often looped. Hook text on screen in the first second.
- Our edge is real Korean ranking data and Seoul prices: lean on "actually #1 in Korea" and "what Koreans pay".

## Caption
- First line = the hook in words (it shows under the video). Then the 5→1 list or the routine steps with Seoul prices.
- End: "Full top 20, Korean prices and where to buy: link in bio, then tap "<chip>" (koreanbeautynow.com). Ranked by Korean reviewers on Hwahae. Not sponsored." The chip names the home-page button for this video (TAP in ops/shorts.mjs, JUMP in build.py): Sunscreen / Toner / Serum / Moisturizer / Cleanser / Masks / Cushion / Lip / Top 20, routine → Full routine, hype → Korea's #1s on Amazon, concern → By concern. The bio link itself must be https://koreanbeautynow.com/ (home, where the chips are).
- Hashtags (6 to 8): always #kbeauty #koreanskincare #hwahae #skincareroutine, plus 2 to 4 for the category:
  - sunscreen: #koreansunscreen #sunscreen #spf
  - toner: #koreantoner #toner #glassskin
  - serum: #koreanserum #serum #glassskin
  - cream: #moisturizer #skinbarrier
  - cleansing: #cleanser #doublecleansing
  - cushion: #cushionfoundation #koreanmakeup
  - lip: #liptint #koreanmakeup
  - masks: #sheetmask #facemask
  - routine: #koreanskincareroutine #glassskin #skinbarrier

## Never
- Post to sdm.check. Claim we tested a product. Show Amazon prices (Associates rules).
