"""Build the K-beauty rankings site from data/latest.json (Hwahae public ranking pages)."""
import html, json, os, re, sys, urllib.parse
from names_en import N
BRANDS = json.load(open(os.path.join(os.path.dirname(__file__), 'brands_en.json')))

BASE = os.environ.get('SITE_BASE', 'https://whistlewhistle311-web.github.io/kbeauty-now/')
OUT = sys.argv[1] if len(sys.argv) > 1 else 'site'
KRW_PER_USD = 1337  # Gumroad's KRW conversion on 2026-10-29 ($9 = 12,032 KRW)
esc = html.escape

CAT = {  # slug: (title, h1 noun, blurb)
    'all': ('All categories', 'K-beauty products', 'The top 20 across every category on Hwahae.'),
    'skincare': ('Skincare', 'Korean skincare products', 'Toners, serums, creams and more.'),
    'toner': ('Toner', 'Korean toners', 'Toners and toner pads.'),
    'serum': ('Serum and essence', 'Korean serums and essences', 'Serums, essences and ampoules.'),
    'cream': ('Cream', 'Korean moisturizers', 'Creams and moisturizers.'),
    'cleansing': ('Cleansing', 'Korean cleansers', 'Foams, oils and cleansing milks.'),
    'masks': ('Masks', 'Korean face masks', 'Sheet masks, wash-off and modeling masks.'),
    'sunscreen': ('Sunscreen', 'Korean sunscreens', 'Chemical and mineral sunscreens.'),
    'cushion': ('Cushion', 'Korean cushion foundations', 'Cushion compacts with SPF.'),
    'lip': ('Lip', 'Korean lip products', 'Tints, balms and lip masks.'),
}
SKIN = {'dry': 'dry skin', 'oily': 'oily skin', 'combination': 'combination skin', 'sensitive': 'sensitive skin', 'acne-prone': 'acne-prone skin'}

CSS = """
:root{--ink:#22201d;--muted:#6b665f;--line:#e6e1da;--bg:#fbf8f4;--card:#fff;--accent:#b04a5a;--soft:#f4ede6}
@media (prefers-color-scheme:dark){:root{--ink:#ece7e1;--muted:#a9a29a;--line:#36312c;--bg:#171513;--card:#201d1a;--accent:#e58a98;--soft:#2a2521}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans KR",sans-serif}
main{max-width:880px;margin:0 auto;padding:28px 16px 72px}
header.top{border-bottom:1px solid var(--line);background:var(--card)}
header.top div{max-width:880px;margin:0 auto;padding:12px 16px;display:flex;gap:14px;flex-wrap:wrap;font-size:14px}
header.top a{color:var(--ink);text-decoration:none}header.top a.home{font-weight:700;margin-right:auto}
h1{font-size:clamp(26px,5.5vw,38px);line-height:1.2;margin:6px 0 10px;letter-spacing:-.02em}
h2{font-size:22px;margin:40px 0 10px}
.lede{color:var(--muted);font-size:17px}.meta{font-size:13px;color:var(--muted)}
.kicker{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);font-weight:700}
ol.rank{list-style:none;padding:0;margin:0}
ol.rank li{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 14px 12px;margin:10px 0;display:grid;grid-template-columns:44px 1fr;gap:4px 12px}
.n{font-size:22px;font-weight:700;color:var(--accent);line-height:1.1}.d{font-size:12px;color:var(--muted)}
.pn{font-weight:650}.ko{word-break:keep-all;color:var(--muted);font-size:14px}
.facts{font-size:14px}.tags span{display:inline-block;background:var(--soft);border-radius:99px;padding:1px 9px;margin:4px 6px 0 0;font-size:12.5px}
.links{font-size:13.5px;margin-top:6px}
a.buy,.card a.buy{display:inline-block;background:var(--accent);color:var(--card)!important;text-decoration:none;font-weight:650;border-radius:10px;padding:10px 18px}.links a{color:var(--accent);margin-right:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.card h3{margin:0 0 6px;font-size:17px}.card a{color:var(--accent)}
.card ol{margin:6px 0 0;padding-left:20px;font-size:14px}
footer{border-top:1px solid var(--line);margin-top:56px;padding-top:14px;font-size:12.5px;color:var(--muted)}
a{color:var(--accent)}
"""


def brand_en(r):
    b = r['brand'] or ''
    return BRANDS.get(b) or (r['brandEn'] if r['brandEn'] and r['brandEn'][0].isupper() and b in r.get('_known', '') else None)


def brand_label(r):
    b = r['brand'] or ''
    if b in BRANDS:
        return BRANDS[b]
    en = r.get('brandEn')
    if r.get('brandOfficial'):
        return en or b
    # romanizer output for unknown brands is a transliteration, not an official name: show it with the Korean
    return f'{en} ({b})' if en and en != b else b


def name_label(r):
    return N.get(r['name']) or r['name']


def usd(krw):
    return f'≈ ${krw / KRW_PER_USD:,.0f}' if krw else ''


AWIN_AFFID = '3138543'
AWIN_ALL = {'yesstyle': '15448'}  # YesStyle UK on Awin (applied 2026-10-29)
_here = os.path.dirname(os.path.abspath(__file__))
try:  # only use Awin links once Awin itself reports the programme as joined (ops/awin_sync.py, hourly)
    _joined = {str(p['id']) for p in json.load(open(os.path.join(_here, 'data', 'awin_stats.json'))).get('joined', [])}
except Exception:
    _joined = set()
AWIN_MID = {k: v for k, v in AWIN_ALL.items() if v in _joined}
try:
    AMAZON_TAG = open(os.path.join(_here, 'ops', 'amazon_tag.txt')).read().strip()
except Exception:
    AMAZON_TAG = ''
LINK_NOTE = ('Store links are search links. Some are affiliate links: we may earn a commission at no extra cost to you, and it never changes the ranking order.'
             if (any(AWIN_MID.values()) or AMAZON_TAG) else 'Store links are search links.')
if AMAZON_TAG:
    LINK_NOTE += ' As an Amazon Associate, K-Beauty Now earns from qualifying purchases.'


def amazon(q):
    return f'https://www.amazon.com/s?k={urllib.parse.quote_plus(q)}&tag={AMAZON_TAG}'


def awin(url, shop):
    mid = AWIN_MID.get(shop)
    if not mid:
        return url, 'nofollow'
    return (f'https://www.awin1.com/cread.php?awinmid={mid}&awinaffid={AWIN_AFFID}&ued=' + urllib.parse.quote(url, safe=''),
            'sponsored nofollow')


def buy_button(r):
    q = f"{brand_label(r).split(' (')[0]} {name_label(r).split(' SPF')[0].split(' (')[0]}"
    if AMAZON_TAG:
        return (f'<p style="margin:12px 0 4px"><a class="buy" href="{esc(amazon(q))}" rel="sponsored nofollow">Check price on Amazon</a></p>'
                '<p class="meta" style="margin:0">Affiliate link: as an Amazon Associate we earn from qualifying purchases.</p>')
    url, rel = awin('https://www.yesstyle.com/en/list.html?q=' + urllib.parse.quote(q), 'yesstyle')
    return f'<p style="margin:12px 0 4px"><a class="buy" href="{esc(url)}" rel="{rel}">Check price on YesStyle</a></p>'


def search_links(r):
    q = f"{brand_label(r).split(' (')[0]} {name_label(r).split(' SPF')[0].split(' (')[0]}"
    oy = 'https://global.oliveyoung.com/display/search?query=' + urllib.parse.quote(q)
    ys, ys_rel = awin('https://www.yesstyle.com/en/list.html?q=' + urllib.parse.quote(q), 'yesstyle')
    amz = f'<a href="{esc(amazon(q))}" rel="sponsored nofollow">Amazon</a>' if AMAZON_TAG else ''
    return f'{amz}<a href="{oy}" rel="nofollow">Olive Young Global</a><a href="{esc(ys)}" rel="{ys_rel}">YesStyle</a><a href="{esc(r["url"])}" rel="nofollow">Hwahae page (KR)</a>'


def delta(r):
    if r['isNew']:
        return 'new'
    d = r['delta']
    if not d:
        return '–'
    return f'▲{d}' if d > 0 else f'▼{-d}'


def row_html(r):
    price = f"₩{r['priceKrw']:,} {usd(r['priceKrw'])}" if r['priceKrw'] else ''
    tags = ''.join(f'<span>{esc(t)}</span>' for t in r['topics'])
    ko = '' if name_label(r) == r['name'] else f'<div class="ko">{esc(r["brand"])} {esc(r["name"])}</div>'
    return f"""<li><div><div class="n">{r['rank']}</div><div class="d">{delta(r)}</div></div>
<div><div class="pn"><a href="{BASE}p/{r['id']}/" style="color:inherit;text-decoration:none">{esc(brand_label(r))} · {esc(name_label(r))}</a></div>{ko}
<div class="facts">★ {r['rating']:.2f} · {r['reviews']:,} reviews{(' · ' + esc(r['size'])) if r['size'] else ''}{(' · ' + price) if price else ''}</div>
<div class="tags">{tags}</div><div class="links">{search_links(r)}</div></div></li>"""


def default_img(path, updated):
    slug = path.strip('/').split('/')[-1]
    if path.startswith('guide/') and slug in GUIDE_PINS:
        return f'guide-{slug}-{updated[:7]}.jpg'
    return f'category-all-{updated[:10]}.jpg'


def page(title, desc, path, body, updated, head=''):
    url = BASE + path
    nav = ''.join(f'<a href="{BASE}c/{s}/">{v[0]}</a>' for s, v in CAT.items() if s in ('skincare', 'sunscreen', 'serum', 'toner', 'cushion'))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="google-site-verification" content="0oISjJafxIxC-LdVeihPqTQ3o9DoxV5FSNgvVZB-tps">
<meta name="p:domain_verify" content="62fc4bdb9182a51a7a89f9e270417f58"/>
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:type" content="article"><meta property="og:site_name" content="K-Beauty Now">
<meta property="article:modified_time" content="{esc(updated[:10])}"><meta property="article:author" content="K-Beauty Now">{head or f'<meta property="og:image" content="{BASE}pins/{default_img(path, updated)}">'}
<style>{CSS}</style></head><body>
<header class="top"><div><a class="home" href="{BASE}">K-Beauty Now</a>{nav}<a href="{BASE}trending/">Trending</a><a href="{BASE}brand/">Brands</a><a href="{BASE}guide/">Guides</a><a href="{BASE}about/">About</a></div></header>
<main>{body}
<footer>Rankings come from the public ranking pages of Hwahae (화해), Korea's largest cosmetics review app, and are refreshed daily. Ranking updated {esc(updated)} KST.
Product names are translated by K-Beauty Now; brand names marked with Korean in brackets are transliterations, not official English names. Prices are Hwahae list prices in Korea; USD is approximate at {KRW_PER_USD:,} KRW per USD.
Need this data as JSON for your shop or trend report? The same rankings are available as an API on <a href="https://apify.com/koreadata-lab/hwahae-kbeauty-ranking-tracker">Apify (Hwahae K-Beauty Ranking Tracker)</a>.
{LINK_NOTE} K-Beauty Now is independent and is not run by Hwahae, Olive Young or YesStyle.</footer></main></body></html>"""


def ranking_page(rk, updated):
    rows = ''.join(row_html(r) for r in rk['rows'])
    if rk['type'] == 'category':
        t, noun, blurb = CAT[rk['slug']]
        h1 = f'Top 20 {noun} in Korea right now'
        title = f'Best {noun} in Korea: Hwahae Top 20 ({updated[:10]})'
        desc = f'The 20 best-ranked {noun.lower()} on Hwahae, Korea\'s biggest cosmetics review app, with English names, ratings, review counts, prices and what reviewers praise.'
        path = f"c/{rk['slug']}/"
    else:
        sk = SKIN[rk['slug']]
        h1 = f'Best Korean skincare for {sk}, ranked by Korean reviewers'
        title = f'Best Korean Skincare for {sk.title()}: Hwahae Top 20 ({updated[:10]})'
        desc = f'Top 20 Korean skincare products for {sk} on Hwahae, ranked from reviews by people with {sk}. English names, ratings and prices.'
        path = f"skin/{rk['slug']}/"
        blurb = f'Ranked using reviews from Hwahae users who registered {sk}.'
    body = f"""<p class="kicker">Hwahae ranking · updated {esc(updated[:10])}</p><h1>{esc(h1)}</h1>
<p class="lede">{esc(blurb)} Rank changes are Hwahae's own movement since the previous ranking. Tags are the review topics Korean users mention most.</p>
<ol class="rank">{rows}</ol>"""
    ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': h1, 'itemListOrder': 'https://schema.org/ItemListOrderAscending',
          'numberOfItems': len(rk['rows']),
          'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f"{BASE}p/{r['id']}/", 'name': f"{brand_label(r)} {name_label(r)}"}
                              for i, r in enumerate(rk['rows'])]}
    img = f"{BASE}pins/{rk['type']}-{rk['slug']}-{updated[:10]}.jpg"
    head = (f'<meta property="og:image" content="{img}"><meta name="twitter:card" content="summary_large_image">'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")}</script>')
    return path, page(title, desc, path, body, updated, head)


def product_pages(data):
    """One page per product ever ranked. Products that drop out keep their page (marked with the last date seen)
    so indexed URLs never 404. History lives in data/products.json."""
    hist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'products.json')
    hist = json.load(open(hist_path)) if os.path.exists(hist_path) else {}
    today = data['updatedAt'][:10]
    prods = {}
    for rk in data['rankings']:
        label = CAT[rk['slug']][0] if rk['type'] == 'category' else f"Skincare for {SKIN[rk['slug']]}"
        href = f"{BASE}c/{rk['slug']}/" if rk['type'] == 'category' else f"{BASE}skin/{rk['slug']}/"
        for i, r in enumerate(rk['rows']):
            p = prods.setdefault(str(r['id']), {'r': r, 'ranks': [], 'near': []})
            p['ranks'].append((label, href, r['rank']))
            for j in (range(max(0, i - 2), min(len(rk['rows']), i + 3)) if rk['slug'] not in ('all', 'skincare') else ()):
                o = rk['rows'][j]
                if o['id'] != r['id'] and all(str(o['id']) != n['id'] for n in p['near']):
                    p['near'].append({'id': str(o['id']), 'name': f"{brand_label(o).split(' (')[0]} {name_label(o)}"})
    for pid, p in prods.items():
        hist[pid] = {'r': p['r'], 'ranks': p['ranks'], 'near': p['near'][:6], 'last': today}
    json.dump(hist, open(hist_path, 'w'), ensure_ascii=False)
    pages = {}
    for pid, h in hist.items():
        r, current = h['r'], h['last'] == today
        nm = f"{brand_label(r).split(' (')[0]} {name_label(r)}"
        ranks = ''.join(f'<li>#{rk} in <a href="{hh}">{esc(l)}</a></li>' for l, hh, rk in sorted(h['ranks'], key=lambda x: x[2]))
        tags = ''.join(f'<span>{esc(t)}</span>' for t in r['topics'])
        price = f"₩{r['priceKrw']:,} ({usd(r['priceKrw'])})" if r['priceKrw'] else 'not listed'
        praise = ''
        if r['topics']:
            tl = [t.lower() for t in r['topics'][:3]]
            praise = (f"<h2>What Korean reviewers say</h2><p>On Hwahae, the topics Korean users mention most for this product are "
                      f"{esc(', '.join(tl[:-1]) + (' and ' if len(tl) > 1 else '') + tl[-1])}. "
                      f"With {r['reviews']:,} reviews and an average of {r['rating']:.2f} out of 5, it is "
                      f"{'one of the most reviewed products in its category' if r['reviews'] >= 5000 else 'a well-rated pick with a smaller review base'}.</p>")
        status = (f"<h2>Where it ranks in Korea today</h2><ul>{ranks}</ul>" if current else
                  f"<h2>Ranking history</h2><p>This product was last in a Hwahae top 20 on {esc(h['last'])}, where it ranked:</p><ul>{ranks}</ul>"
                  f"<p>It is not in today's top 20. See <a href=\"{BASE}\">today's rankings</a>.</p>")
        near = ''.join(f'<li><a href="{BASE}p/{n["id"]}/">{esc(n["name"])}</a></li>' for n in h['near'] if n['id'] in hist)
        near = f'<h2>Ranked near it</h2><ul>{near}</ul>' if near else ''
        bl = brand_label(r).split(' (')[0]
        bcount = sum(1 for x in hist.values() if brand_label(x['r']).split(' (')[0] == bl)
        blink = f'<p class="meta">More from this brand: <a href="{BASE}brand/{brand_slug(bl)}/">best {esc(bl)} products</a></p>' if bcount >= 2 else ''
        body = f"""<p class="kicker">Hwahae ranking profile</p><h1>{esc(nm)}</h1>
<p class="ko">{esc(r['brand'])} {esc(r['name'])}</p>
<div class="card"><div class="facts">★ <strong>{r['rating']:.2f}</strong> on Hwahae from {r['reviews']:,} Korean reviews</div>
<div class="facts">Korean list price: {price}{(' · ' + esc(r['size'])) if r['size'] else ''}</div>
<div class="tags">{tags}</div>{buy_button(r)}<div class="links">{search_links(r)}</div></div>
{praise}{status}{near}{blink}
<h2>Buying it outside Korea</h2><p>Hwahae prices are Korean list prices; international shops usually charge more after shipping. Check the size matches ({esc(r['size']) if r['size'] else 'sizes vary by market'}) and buy from authorised sellers to avoid fakes.</p>
<p class="meta">Tags are the review topics Korean Hwahae users mention most for this product. Ratings and ranks change daily.</p>"""
        title = f"{nm}: Hwahae Rating {r['rating']:.2f} and Korea Ranking"
        desc = f"{nm} is rated {r['rating']:.2f} from {r['reviews']:,} Korean reviews on Hwahae. See where it ranks in Korea, its Korean price and what reviewers praise."
        pages[f"p/{pid}/"] = page(title, desc, f"p/{pid}/", body, data['updatedAt'])
    pages.update(brand_pages(hist, today, data['updatedAt']))
    return pages


def brand_slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def brand_pages(hist, today, updated):
    """One page per brand with 2+ products ever ranked on Hwahae, plus a brand index."""
    groups = {}
    for pid, h in hist.items():
        b = brand_label(h['r']).split(' (')[0]
        groups.setdefault(b, []).append((pid, h))
    pages, idx = {}, []
    for b, items in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        slug = brand_slug(b)
        if len(items) < 2 or not slug:
            continue
        items.sort(key=lambda t: (t[1]['last'] != today, min(x[2] for x in t[1]['ranks']), -t[1]['r']['reviews']))
        ko = items[0][1]['r']['brand']
        live = sum(1 for _, h in items if h['last'] == today)
        reviews = sum(h['r']['reviews'] for _, h in items)
        cards = []
        for pid, h in items:
            r = h['r']
            best = min(h['ranks'], key=lambda x: x[2])
            where = f'#{best[2]} in <a href="{best[1]}">{esc(best[0])}</a>' + ('' if h['last'] == today else f' (last seen {esc(h["last"])})')
            q = f"{b} {name_label(r).split(' SPF')[0].split(' (')[0]}"
            amz = f'<a class="buy" href="{esc(amazon(q))}" rel="sponsored nofollow">See it on Amazon</a>' if AMAZON_TAG else ''
            tg = ', '.join(t.lower() for t in r['topics'][:3])
            cards.append(f'<div class="card"><p class="kicker">{where}</p><h3><a href="{BASE}p/{pid}/">{esc(name_label(r))}</a></h3>'
                         f'<p class="meta">★ {r["rating"]:.2f} from {r["reviews"]:,} Korean reviews' + (f'. Reviewers mention: {esc(tg)}.' if tg else '.') + f'</p><p>{amz}</p></div>')
        shop = (f'<p><a class="buy" href="{esc(amazon(b + " korean skincare"))}" rel="sponsored nofollow">Shop {esc(b)} on Amazon</a></p>' if AMAZON_TAG else '')
        body = (f'<p class="kicker">Brand · updated {esc(updated[:10])}</p><h1>Best {esc(b)} products, ranked by Korean reviewers</h1>'
                f'<p class="ko">{esc(ko)}</p>'
                f'<p class="lede">{len(items)} {esc(b)} products have made a Hwahae top 20 (Korea\'s biggest cosmetics review app) since we started tracking, '
                f'{live} of them today. Together they carry {reviews:,} Korean reviews. Best-ranked first.</p>{shop}'
                f'<div class="grid">{"".join(cards)}</div><p class="meta">{esc(LINK_NOTE)}</p>'
                f'<p><a href="{BASE}brand/">All brands</a> · <a href="{BASE}">Today\'s rankings</a></p>')
        ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': f'Best {b} products on Hwahae',
              'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f"{BASE}p/{pid}/"} for i, (pid, _) in enumerate(items)]}
        head = f'<meta property="og:image" content="{BASE}pins/category-all-{updated[:10]}.jpg"><script type="application/ld+json">{json.dumps(ld).replace("</", "<\\/")}</script>'
        pages[f'brand/{slug}/'] = page(f'Best {b} Products (Updated Daily): Ranked by Korean Reviewers on Hwahae',
                                       f'The {b} ({ko}) products Korean reviewers rank highest on Hwahae, with ratings, review counts and what they praise. Updated daily.',
                                       f'brand/{slug}/', body, updated, head)
        idx.append((b, slug, len(items), live))
    lst = ''.join(f'<div class="card"><h3><a href="{BASE}brand/{sl}/">{esc(b)}</a></h3><p class="meta">{n} ranked products, {lv} in today\'s top 20s</p></div>' for b, sl, n, lv in idx)
    pages['brand/'] = page('Korean Skincare Brands Ranked by Korean Reviewers (Hwahae)',
                           'Every Korean beauty brand with several products in Hwahae\'s top 20 rankings, with their best-rated products. Updated daily.',
                           'brand/', f'<p class="kicker">Brands</p><h1>Korean beauty brands Korean reviewers rank highest</h1><p class="lede">Brands with two or more products in a Hwahae top 20. Click a brand for its best-ranked products.</p><div class="grid">{lst}</div>', updated)
    return pages


GUIDES = {
    'korean-toner': ('toner', 'Best Korean Toner (Updated Daily): What Koreans Pick on Hwahae',
        'Toner, toner pad or essence toner? How Korean toners work and the 5 toners Korean Hwahae users rank highest today.',
        'Best Korean toner: what Koreans pick, and how to choose',
        'In Korea a toner is not an astringent: it is the first hydrating step after cleansing. Here is how to pick one, and the five toners Korean Hwahae users rank highest today.',
        '<h2>Three kinds of Korean toner</h2><ul><li><b>Hydrating toner</b> (스킨/토너): watery, applied with hands or a cotton pad right after cleansing.</li>'
        '<li><b>Toner pad</b> (토너패드): pre-soaked pads, often with mild exfoliating acids (PHA, LHA) or soothing extracts. Good for a quick routine.</li>'
        '<li><b>Essence toner</b>: thicker, sits between toner and serum. Useful for dry skin.</li></ul>'
        '<h2>How to choose</h2><p>Dry skin: look for glycerin, panthenol or hyaluronic acid. Oily or acne-prone skin: lighter toners or pads with PHA/BHA, used a few times a week. Sensitive skin: short ingredient lists, mugwort (쑥) or centella (병풀). Check the review tags under each product: Korean users often mention Soothing, Moisturizing or Non-sticky.</p>'),
    'korean-serum': ('serum', 'Best Korean Serum and Ampoule (Updated Daily): Hwahae Top Picks',
        'Serum, essence or ampoule? What the Korean terms mean and the 5 serums Korean Hwahae users rank highest today.',
        'Best Korean serum: what Koreans pick, and how to choose',
        'Korean brands use serum, essence and ampoule for similar products. Here is what the words usually mean, and the five serums Korean Hwahae users rank highest today.',
        '<h2>Serum, essence, ampoule</h2><p>There is no legal difference. In practice an <b>essence</b> is lighter, a <b>serum</b> is a little thicker, and an <b>ampoule</b> is marketed as the most concentrated. Choose by the active ingredient, not the word.</p>'
        '<h2>Common Korean serum ingredients</h2><ul><li>Niacinamide: tone and oil control.</li><li>Vitamin C: brightening; can sting sensitive skin.</li><li>Centella, mugwort, heartleaf (어성초): soothing.</li><li>Retinal or retinol: anti-ageing; use at night and wear sunscreen by day.</li><li>Hyaluronic acid, panthenol: hydration.</li></ul>'),
    'korean-moisturizer': ('cream', 'Best Korean Moisturizer (Updated Daily): Hwahae Top Creams',
        'How to choose a Korean cream for dry, oily or sensitive skin, and the 5 creams Korean Hwahae users rank highest today.',
        'Best Korean moisturizer: what Koreans pick, and how to choose',
        'The cream is the step that seals in the toner and serum. Here is how to choose by skin type, and the five creams Korean Hwahae users rank highest today.',
        '<h2>Choose by texture</h2><ul><li><b>Gel cream</b>: light, good for oily skin and hot weather.</li><li><b>Barrier cream</b> with ceramides: for dry or irritated skin, and for winter.</li><li><b>Soothing cream</b> with centella or panthenol: for redness and sensitive skin.</li></ul>'
        '<p>For skin-type rankings, see <a href="https://whistlewhistle311-web.github.io/kbeauty-now/skin/dry/">dry skin</a>, <a href="https://whistlewhistle311-web.github.io/kbeauty-now/skin/oily/">oily skin</a> and <a href="https://whistlewhistle311-web.github.io/kbeauty-now/skin/sensitive/">sensitive skin</a>.</p>'),
    'korean-cleanser': ('cleansing', 'Best Korean Cleanser (Updated Daily): Double Cleansing Picks from Hwahae',
        'Korean double cleansing explained (oil first, then foam) and the 5 cleansers Korean Hwahae users rank highest today.',
        'Best Korean cleanser: what Koreans pick, and how to double cleanse',
        'Koreans usually cleanse twice at night: an oil or balm to remove sunscreen and makeup, then a water-based cleanser. Here is how, and the five cleansers Korean Hwahae users rank highest today.',
        '<h2>Double cleansing in two steps</h2><ol><li><b>Oil, balm or cleansing water</b> (클렌징 오일/밤/워터) on dry skin, then rinse. This removes sunscreen and makeup.</li><li><b>Foam or gel cleanser</b> (폼클렌저) to remove sweat and the oil residue.</li></ol>'
        '<p>In the morning one gentle cleanser is enough. If your skin feels tight after washing, pick a low-pH or "mild" foam; Korean reviews often tag these as Gentle or Not drying.</p>'),
}


GUIDE_PINS = {  # evergreen pins, refreshed monthly (guid changes each month)
    'korean-skincare-routine': ('sunscreen', 'Korean skincare routine in 5 steps', ['1. Cleanse (oil first at night)', '2. Hydrating toner', '3. One serum', '4. Moisturizer', '5. SPF50+ sunscreen every morning']),
    'korean-sunscreen': ('sunscreen', 'How to choose a Korean sunscreen', ['PA++++ is the top UVA grade.', 'Mineral (무기자차) suits sensitive skin.', 'Chemical (유기자차) feels lighter.', 'Look for the No white cast tag.']),
    'korean-toner': ('toner', 'How to choose a Korean toner', ['Korean toner hydrates, it is not an astringent.', 'Toner pads with PHA: quick gentle exfoliation.', 'Dry skin: glycerin, panthenol, hyaluronic acid.', 'Sensitive skin: centella or mugwort.']),
    'korean-serum': ('serum', 'Korean serum, essence or ampoule?', ['The names have no legal difference.', 'Pick by active ingredient, not the word.', 'Niacinamide: tone and oil control.', 'Centella, heartleaf: soothing.']),
    'korean-moisturizer': ('cream', 'How to choose a Korean moisturizer', ['Gel cream: oily skin, hot weather.', 'Ceramide barrier cream: dry skin, winter.', 'Centella or panthenol: redness.', 'Seal in toner and serum with it.']),
    'korean-skincare-on-amazon': ('cream', 'Best Korean skincare on Amazon, picked by Korean reviewers', ['Start from what Koreans rate highest.', 'Buy from the brand store or Ships from Amazon.', 'Two top picks per routine step.', 'Updated daily from Hwahae.']),
    'korean-cleanser': ('cleansing', 'Korean double cleansing in 2 steps', ['1. Oil or balm on dry skin, then rinse.', '2. Foam or gel cleanser.', 'Morning: one gentle cleanser is enough.', 'Tight after washing? Try a low-pH foam.']),
}

for _k, _t, _need, _avoid, _key in [
    ('dry', 'dry skin', 'Layer hydration: a hydrating toner (patted in two or three times), a serum with hyaluronic acid or panthenol, then a ceramide cream. Look for the review tags Moisturizing and Fixes inner dryness.', 'Foaming cleansers that leave skin tight, and alcohol-heavy toners.', 'Ceramides, panthenol, glycerin, squalane'),
    ('oily', 'oily skin', 'Keep it light: a gel cleanser, a watery toner or a toner pad with PHA or BHA a few times a week, niacinamide serum and a gel cream. Oily skin still needs moisture, or it makes more oil.', 'Skipping moisturizer, and heavy balm cleansers left on the skin.', 'Niacinamide, BHA (salicylic acid), heartleaf, green tea'),
    ('combination', 'combination skin', 'Treat zones differently: a light gel cream all over and a richer cream only on dry cheeks. A gentle low-pH cleanser keeps both areas balanced.', 'Using strong oil-control products on dry areas.', 'Niacinamide, hyaluronic acid, panthenol'),
    ('sensitive', 'sensitive skin', 'Fewer products, shorter ingredient lists, patch test first. Korean brands make many soothing lines with centella (병풀) or mugwort (쑥). Mineral sunscreens (무기자차) are usually gentler.', 'Fragrance, essential oils, strong acids and high-dose vitamin C.', 'Centella, mugwort, panthenol, madecassoside'),
    ('acne-prone', 'acne-prone skin', 'Gentle cleansing twice a day, a BHA or heartleaf toner, and light non-comedogenic moisturizer. Do not skip sunscreen: it helps marks fade.', 'Over-washing, scrubs, and heavy oils on breakout areas.', 'BHA, heartleaf (어성초), tea tree, niacinamide, azelaic acid'),
]:
    GUIDES[f'skincare-for-{_k}-skin'] = (f'skin:{_k}', f'Best Korean Skincare for {_t.title()} (Updated Daily): Hwahae Top Picks',
        f'How to build a Korean skincare routine for {_t}, which ingredients to look for, and the 5 products Hwahae users with {_t} rank highest today.',
        f'Korean skincare for {_t}: what works, and what Koreans pick',
        f'Hwahae lets users register their skin type, so its rankings show what people with {_t} actually rate highly. Here is how to build a routine for {_t}, and today\'s top 5.',
        f'<h2>How to build the routine</h2><p>{_need}</p><h2>Ingredients to look for</h2><p>{_key}.</p><h2>What to avoid</h2><p>{_avoid}</p>'
        f'<p>New to the order of steps? See the <a href="https://whistlewhistle311-web.github.io/kbeauty-now/guide/korean-skincare-routine/">Korean skincare routine guide</a>.</p>')


def trending(data, n=15):
    """Biggest climbers and new entries across every Hwahae list, one row per product (best move kept)."""
    best = {}
    for rk in data['rankings']:
        where = CAT[rk['slug']][0] if rk['type'] == 'category' else SKIN[rk['slug']].capitalize()
        for r in rk['rows']:
            score = 100 if r['isNew'] else (r['delta'] or 0)
            if score <= 0:
                continue
            if r['id'] not in best or score > best[r['id']][0]:
                best[r['id']] = (score, r, where, rk)
    return sorted(best.values(), key=lambda t: (-t[0], t[1]['rank']))[:n]


def extra_pages(data):
    by = {(rk['type'], rk['slug']): rk for rk in data['rankings']}
    up = data['updatedAt']
    pages = {}
    about = f"""<p class="kicker">About</p><h1>About K-Beauty Now</h1>
<p class="lede">K-Beauty Now shows what Korean shoppers actually rate highly, in English, so you can pick Korean skincare without guessing from ads.</p>
<h2>Where the data comes from</h2>
<p>Every morning we read the public ranking pages of Hwahae (화해), Korea's largest cosmetics review app. Hwahae ranks products from reviews by its users, and splits rankings by category and by the skin type users register. We take the top 20 of each list. We do not use private data, reviewer profiles or review texts.</p>
<h2>What we add</h2>
<ul><li>English product names (translated by us) and official English brand names where we are sure of them. Where we are not sure, the brand is shown as a transliteration with the Korean in brackets.</li>
<li>The review topics Korean users mention most, translated to English (for example Soothing, Non-sticky, No white cast).</li>
<li>Approximate USD prices from Korean list prices.</li></ul>
<h2>What we do not do</h2>
<p>We do not test products ourselves and we do not write fake reviews. Rankings are Hwahae's, not ours. K-Beauty Now is independent and not affiliated with Hwahae.</p>
<h2>Links</h2>
<p>Store links help you find a product abroad. Some links may earn us a commission at no extra cost to you; this never changes the ranking order, which comes straight from Hwahae.</p>"""
    pages['about/'] = page('About K-Beauty Now: How We Rank Korean Skincare', 'How K-Beauty Now turns Hwahae, Korea\'s biggest cosmetics review app, into daily English rankings.', 'about/', about, up)
    sun = by.get(('category', 'sunscreen'))
    if sun:
        top = ''.join(row_html(r) for r in sun['rows'][:5])
        g = f"""<p class="kicker">Guide · updated {esc(up[:10])}</p><h1>Best Korean sunscreen: what Koreans pick, and how to choose</h1>
<p class="lede">Korean sunscreens are known for light textures and high protection. Here is how to read the labels, and the five sunscreens Korean Hwahae users rank highest today.</p>
<h2>SPF50+ and PA++++</h2>
<p>SPF measures protection from UVB (burning). PA measures protection from UVA (ageing and darkening); PA++++ is the highest grade on Korean labels. Most top Korean sunscreens are SPF50+ PA++++.</p>
<h2>Mineral or chemical?</h2>
<p>Korean labels call mineral (physical) sunscreens 무기자차 and chemical ones 유기자차. Mineral filters (zinc oxide, titanium dioxide) suit sensitive skin but can leave a white cast. Chemical filters feel lighter. Look for the review tag "No white cast" if that matters to you.</p>
<h2>Top 5 on Hwahae today</h2><ol class="rank">{top}</ol>
<p><a href="{BASE}c/sunscreen/">See the full top 20 Korean sunscreens</a></p>"""
        pages['guide/korean-sunscreen/'] = page('Best Korean Sunscreen (Updated Daily): SPF50+ PA++++ Picks from Hwahae', 'How to choose a Korean sunscreen (SPF50+, PA++++, mineral vs chemical) and the 5 sunscreens Korean Hwahae users rank highest today.', 'guide/korean-sunscreen/', g, up)

    for slug, (cat, title, desc, h1, lede, body) in GUIDES.items():
        kind, key = ('skin', cat[5:]) if cat.startswith('skin:') else ('category', cat)
        rk = by.get((kind, key))
        if not rk:
            continue
        top = ''.join(row_html(r) for r in rk['rows'][:5])
        more = (f'<a href="{BASE}c/{key}/">See the full top 20 {CAT[key][1]}</a>' if kind == 'category'
                else f'<a href="{BASE}skin/{key}/">See the full top 20 for {SKIN[key]}</a>')
        h2 = 'Top 5 on Hwahae today' if kind == 'category' else f'Top 5 for {SKIN[key]} on Hwahae today'
        g = (f'<p class="kicker">Guide · updated {esc(up[:10])}</p><h1>{h1}</h1><p class="lede">{lede}</p>{body}'
             f'<h2>{h2}</h2><ol class="rank">{top}</ol><p>{more}</p>')
        pages[f'guide/{slug}/'] = page(title, desc, f'guide/{slug}/', g, up)
    steps = [('cleansing', 'Cleanse', 'Oil or balm at night to remove sunscreen, then a foam or gel cleanser. In the morning one gentle cleanser is enough.'),
             ('toner', 'Toner', 'A hydrating toner right after washing, by hand or on a cotton pad. Toner pads with PHA can replace it a few times a week.'),
             ('serum', 'Serum or essence', 'One targeted treatment: niacinamide for tone and oil, centella or heartleaf for redness, vitamin C for dullness.'),
             ('cream', 'Moisturizer', 'Seal everything in. Gel cream if you are oily, a ceramide cream if you are dry.'),
             ('sunscreen', 'Sunscreen (morning)', 'SPF50+ PA++++ every morning, even indoors near windows. This is the step Koreans never skip.')]
    blocks = []
    for i, (cat, name, txt) in enumerate(steps, 1):
        rk = by.get(('category', cat))
        pick = ''
        if rk:
            r = rk['rows'][0]
            noun = {'cleansing': 'cleanser', 'toner': 'toner', 'serum': 'serum', 'cream': 'moisturizer', 'sunscreen': 'sunscreen'}[cat]
            pick = (f'<p class="meta">Korea\'s #1 {noun} on Hwahae today: <a href="{BASE}p/{r["id"]}/">{esc(brand_label(r))} {esc(name_label(r))}</a></p>'
                    f'<p class="links">{search_links(r)}<a href="{BASE}c/{cat}/">Top 20</a></p>')
        blocks.append(f'<h2>{i}. {name}</h2><p>{txt}</p>{pick}')
    routine = (f'<p class="kicker">Guide · updated {esc(up[:10])}</p><h1>Korean skincare routine: the order that actually matters</h1>'
               '<p class="lede">Forget the 10-step myth. Most Koreans use four or five steps. Here is the order, what each step does, and the product Korean Hwahae users rank #1 for each step today.</p>'
               + ''.join(blocks) +
               '<h2>Optional extras</h2><p>Sheet masks once or twice a week after toner. Eye cream before moisturizer. Exfoliating pads or acids two or three nights a week, never on the same night as retinol.</p>'
               f'<h2>By skin type</h2><p>' + ' · '.join(f'<a href="{BASE}guide/skincare-for-{k}-skin/">{v}</a>' for k, v in SKIN.items()) + '</p>')
    pages['guide/korean-skincare-routine/'] = page('Korean Skincare Routine Order (Updated Daily): 5 Steps and Korea\'s #1 Pick for Each',
        'The Korean skincare routine in the right order: cleanser, toner, serum, moisturizer, sunscreen, with the product Korean Hwahae users rank #1 for each step today.',
        'guide/korean-skincare-routine/', routine, up)
    movers = trending(data)
    if movers:
        items = ''.join(
            f'<li><div><div class="n">{r["rank"]}</div><div class="d">{delta(r)}</div></div><div>'
            f'<div class="pn"><a href="{BASE}p/{r["id"]}/" style="color:inherit;text-decoration:none">{esc(brand_label(r))} · {esc(name_label(r))}</a></div>'
            f'<div class="facts">#{r["rank"]} in {esc(where)} · ★ {r["rating"]:.2f} · {r["reviews"]:,} reviews</div>'
            f'<div class="tags">{"".join(f"<span>{esc(t)}</span>" for t in r["topics"])}</div><div class="links">{search_links(r)}</div></div></li>'
            for _, r, where, rk in movers)
        tr = (f'<p class="kicker">Trending · updated {esc(up[:10])}</p><h1>Trending Korean skincare right now: what is climbing in Korea</h1>'
              '<p class="lede">The products moving up fastest across all of Hwahae\'s rankings today, plus new entries. "▲5" means up five places since Hwahae\'s previous ranking. '
              'Products that climb in Korea often reach Western shops and TikTok months later.</p>'
              f'<ol class="rank">{items}</ol><p><a href="{BASE}c/all/">See the overall top 20</a> · <a href="{BASE}guide/">Buying guides</a></p>')
        pages['trending/'] = page('Trending Korean Skincare Right Now: Fastest Climbers on Hwahae (Updated Daily)',
            'The Korean skincare and makeup products climbing fastest on Hwahae, Korea\'s biggest cosmetics review app, today. English names, ratings and where to buy.',
            'trending/', tr, up)
    # Amazon picks: Korea's #1-#2 per routine step, each with an Amazon search button (only when the Amazon tag is set)
    if AMAZON_TAG:
        steps_a = [('sunscreen', 'Sunscreen'), ('toner', 'Toner'), ('serum', 'Serum and essence'), ('cream', 'Moisturizer'),
                   ('cleansing', 'Cleanser'), ('masks', 'Sheet masks and pads'), ('cushion', 'Cushion foundation')]
        secs = []
        for cat, label in steps_a:
            rk = by.get(('category', cat))
            if not rk:
                continue
            cards = []
            for r in rk['rows'][:2]:
                q = f"{brand_label(r).split(' (')[0]} {name_label(r).split(' SPF')[0].split(' (')[0]}"
                tags = ', '.join(t.lower() for t in r['topics'][:3])
                cards.append(f'<div class="card"><p class="kicker">#{r["rank"]} {esc(label.lower())} in Korea</p>'
                             f'<h3><a href="{BASE}p/{r["id"]}/">{esc(brand_label(r))} {esc(name_label(r))}</a></h3>'
                             f'<p class="meta">★ {r["rating"]:.2f} from {r["reviews"]:,} Korean reviews' + (f'. Reviewers mention: {esc(tags)}.' if tags else '.') + '</p>'
                             f'<p><a class="buy" href="{esc(amazon(q))}" rel="sponsored nofollow">See it on Amazon</a></p></div>')
            secs.append(f'<h2>{esc(label)}</h2><div class="grid">{"".join(cards)}</div>')
        am = (f'<p class="kicker">Buying guide · updated {esc(up[:10])}</p><h1>Best Korean skincare on Amazon, picked by Korean reviewers</h1>'
              '<p class="lede">Amazon is full of Korean skincare, but its bestseller lists mix in sponsored and Western-made products. '
              'This list starts from the other side: the products Korean shoppers rate highest on Hwahae, Korea\'s biggest cosmetics review app, today, '
              'two per routine step, each linked to an Amazon search so you can compare sellers and prices.</p>'
              '<p class="meta">Check the seller before you buy: look for the brand\'s official store or "Ships from Amazon" to avoid fakes. Formulas sold abroad can differ slightly from the Korean version.</p>'
              + ''.join(secs) +
              f'<p class="meta">{esc(LINK_NOTE)}</p><p><a href="{BASE}guide/korean-skincare-routine/">Korean routine order</a> · <a href="{BASE}trending/">What is trending in Korea</a></p>')
        pages['guide/korean-skincare-on-amazon/'] = page('Best Korean Skincare on Amazon (Updated Daily): Picks from Korean Reviewers',
            'The Korean skincare products Korean reviewers rank highest on Hwahae today, two per routine step, each with a link to find it on Amazon.',
            'guide/korean-skincare-on-amazon/', am, up)
    names = {'korean-sunscreen': 'Korean sunscreen', 'korean-skincare-routine': 'Korean skincare routine order', 'korean-skincare-on-amazon': 'Best Korean skincare on Amazon'} | {k: GUIDES[k][3].split(':')[0].replace('Best ', '') for k in GUIDES}
    hub = '<p class="kicker">Guides</p><h1>Korean skincare buying guides</h1><p class="lede">Short, practical guides to each step of a Korean routine, each with the five products Korean Hwahae users rank highest today.</p><div class="grid">' + ''.join(
        f'<div class="card"><h3><a href="{BASE}{p}">{esc(names.get(p.split("/")[1], p))}</a></h3></div>' for p in sorted((p for p in pages if p.startswith('guide/')), key=lambda p: (p != 'guide/korean-skincare-routine/', 'skin' in p))) + '</div>'
    pages['guide/'] = page('Korean Skincare Buying Guides: Sunscreen, Toner, Serum, Moisturizer, Cleanser', 'Practical guides to each step of a Korean skincare routine, with the products Korean Hwahae users rank highest today.', 'guide/', hub, up)
    return pages


def pins_and_rss(data):
    up = data['updatedAt'][:10]
    import email.utils, datetime
    pub = email.utils.format_datetime(datetime.datetime.fromisoformat(up + 'T06:00:00+09:00'))
    pins, items = [], []
    for rk in data['rankings']:
        if rk['type'] == 'category':
            t = f"Korea's top-rated {CAT[rk['slug']][1].replace('Korean ', '')}"
            href = f"{BASE}c/{rk['slug']}/"
        else:
            t = f"Best Korean skincare for {SKIN[rk['slug']]}"
            href = f"{BASE}skin/{rk['slug']}/"
        f = f"{rk['type']}-{rk['slug']}-{up}.jpg"
        pins.append({'title': t, 'date': up, 'file': f, 'items': [
            {'brand': brand_label(r).split(' (')[0], 'name': name_label(r).split(' SPF')[0].split(' (')[0], 'rating': r['rating'], 'reviews': r['reviews']}
            for r in rk['rows'][:5]]})
        top = ', '.join(f"{brand_label(r).split(' (')[0]} {name_label(r).split(' SPF')[0].split(' (')[0]}" for r in rk['rows'][:3])
        items.append(f"<item><title>{esc(t)} ({up})</title><link>{href}</link><guid isPermaLink=\"false\">{rk['type']}-{rk['slug']}-{up}</guid>"
                     f"<pubDate>{pub}</pubDate><description>{esc('Hwahae top 5 today: ' + top + '. Ranked by Korean reviewers.')}</description>"
                     f"<enclosure url=\"{BASE}pins/{f}\" type=\"image/jpeg\" length=\"0\"/></item>")
    mv = trending(data, 5)
    if len(mv) >= 3:
        f = f"trending-{up}.jpg"
        pins.append({'title': 'Trending in Korea: fastest-climbing K-beauty today', 'date': up, 'file': f, 'items': [
            {'brand': brand_label(r).split(' (')[0], 'name': name_label(r).split(' SPF')[0].split(' (')[0], 'rating': r['rating'], 'reviews': r['reviews']}
            for _, r, _, _ in mv]})
        top = ', '.join(f"{brand_label(r).split(' (')[0]} {name_label(r).split(' SPF')[0].split(' (')[0]} ({delta(r)})" for _, r, _, _ in mv[:3])
        items.append(f"<item><title>Trending Korean skincare right now ({up})</title><link>{BASE}trending/</link><guid isPermaLink=\"false\">trending-{up}</guid>"
                     f"<pubDate>{pub}</pubDate><description>{esc('Climbing fastest on Hwahae today: ' + top + '. What Korea is buying before it trends abroad.')}</description>"
                     f"<enclosure url=\"{BASE}pins/{f}\" type=\"image/jpeg\" length=\"0\"/></item>")
    # product pins: top 3 of each category, refreshed weekly (guid carries the ISO week)
    yr, wk, _ = datetime.date.fromisoformat(up).isocalendar()
    week = f"{yr}-W{wk:02d}"
    done = set()
    for rk in data['rankings']:
        if rk['type'] != 'category' or rk['slug'] in ('all', 'skincare'):
            continue
        noun = CAT[rk['slug']][1].replace('Korean ', '').rstrip('s')
        noun = {'serums and essence': 'serum', 'moisturizer': 'moisturizer', 'face mask': 'face mask'}.get(noun, noun)
        for r in rk['rows'][:3]:
            if r['id'] in done:
                continue
            done.add(r['id'])
            b, n = brand_label(r).split(' (')[0], name_label(r).split(' (')[0]
            f = f"product-{r['id']}-{week}.jpg"
            title = f"{b} {n}: #{r['rank']} Korean {noun} on Hwahae"
            pins.append({'title': title, 'date': up, 'file': f, 'product': {
                'kicker': f"#{r['rank']} {noun} in Korea", 'brand': b, 'name': n, 'ko': f"{r['brand']} {r['name']}",
                'rating': r['rating'], 'reviews': r['reviews'], 'tags': r['topics'][:3], 'price': usd(r['priceKrw']),
                'others': [{'rank': o['rank'], 'name': f"{brand_label(o).split(' (')[0]} {name_label(o).split(' SPF')[0].split(' (')[0]}"}
                           for o in rk['rows'][:4] if o['id'] != r['id']][:3], 'noun': noun}})
            desc = (f"{b} {n} is #{r['rank']} in Korean {noun}s on Hwahae, rated {r['rating']:.2f} from {r['reviews']:,} Korean reviews. "
                    f"Korean reviewers mention: {', '.join(t.lower() for t in r['topics'][:3])}. English name, Korean price and where to buy.")
            items.append(f"<item><title>{esc(title)}</title><link>{BASE}p/{r['id']}/</link><guid isPermaLink=\"false\">product-{r['id']}-{week}</guid>"
                         f"<pubDate>{pub}</pubDate><description>{esc(desc)}</description>"
                         f"<enclosure url=\"{BASE}pins/{f}\" type=\"image/jpeg\" length=\"0\"/></item>")
    month = up[:7]
    by = {(rk['type'], rk['slug']): rk for rk in data['rankings']}
    for slug, (cat, title, tips) in GUIDE_PINS.items():
        rk = by.get(('category', cat))
        if not rk:
            continue
        r = rk['rows'][0]
        pick = f"{brand_label(r).split(' (')[0]} {name_label(r).split(' SPF')[0].split(' (')[0]}"
        f = f"guide-{slug}-{month}.jpg"
        pins.append({'title': title, 'date': up, 'file': f, 'tips': tips, 'pick': pick,
                     'pickLabel': f"Korea's #1 {CAT[cat][0].lower().replace('cleansing', 'cleanser').replace('cream', 'moisturizer').replace('serum and essence', 'serum')} right now (Hwahae)"})
        items.append(f"<item><title>{esc(title)}</title><link>{BASE}guide/{slug}/</link><guid isPermaLink=\"false\">guide-{slug}-{month}</guid>"
                     f"<pubDate>{pub}</pubDate><description>{esc(title + '. ' + ' '.join(tips) + ' Korea' + chr(39) + 's #1 right now: ' + pick + '.')}</description>"
                     f"<enclosure url=\"{BASE}pins/{f}\" type=\"image/jpeg\" length=\"0\"/></item>")
    # brand pins: top brands by number of ranked products, refreshed monthly
    try:
        hist = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'products.json')))
    except Exception:
        hist = {}
    groups = {}
    for pid, h in hist.items():
        groups.setdefault(brand_label(h['r']).split(' (')[0], []).append(h)
    for b, hs in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:8]:
        if len(hs) < 3 or not brand_slug(b):
            continue
        hs.sort(key=lambda h: (min(x[2] for x in h['ranks']), -h['r']['reviews']))
        f = f"brand-{brand_slug(b)}-{month}.jpg"
        pins.append({'title': f'Best {b} products, ranked by Korean reviewers', 'date': up, 'file': f, 'items': [
            {'brand': b, 'name': name_label(h['r']).split(' SPF')[0].split(' (')[0], 'rating': h['r']['rating'], 'reviews': h['r']['reviews']} for h in hs[:5]]})
        top = ', '.join(name_label(h['r']).split(' SPF')[0].split(' (')[0] for h in hs[:3])
        items.append(f"<item><title>{esc('Best ' + b + ' products, ranked by Korean reviewers')}</title><link>{BASE}brand/{brand_slug(b)}/</link><guid isPermaLink=\"false\">brand-{brand_slug(b)}-{month}</guid>"
                     f"<pubDate>{pub}</pubDate><description>{esc(f'{len(hs)} {b} products have made a Hwahae top 20 in Korea. Top picks: {top}. Ratings and review counts from Korean reviewers.')}</description>"
                     f"<enclosure url=\"{BASE}pins/{f}\" type=\"image/jpeg\" length=\"0\"/></item>")
    json.dump({'pins': pins}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pins.json'), 'w'), ensure_ascii=False)
    rss = (f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>K-Beauty Now</title><link>{BASE}</link>'
           f'<description>Korea\'s top-rated K-beauty from Hwahae, in English, updated daily.</description>{"".join(items)}</channel></rss>')
    return rss


def index_page(data):
    up = data['updatedAt']
    cards = []
    for rk in data['rankings']:
        name = CAT[rk['slug']][0] if rk['type'] == 'category' else f"Skincare for {SKIN[rk['slug']]}"
        href = f"{BASE}c/{rk['slug']}/" if rk['type'] == 'category' else f"{BASE}skin/{rk['slug']}/"
        top = ''.join(f'<li><a href="{BASE}p/{r["id"]}/" style="color:inherit">{esc(brand_label(r).split(" (")[0])} {esc(name_label(r).split(" SPF")[0])}</a></li>' for r in rk['rows'][:5])
        cards.append(f'<div class="card"><h3><a href="{href}">{esc(name)}</a></h3><ol>{top}</ol></div>')
    body = f"""<p class="kicker">Updated daily from Hwahae</p><h1>What Koreans are actually buying in K-beauty</h1>
<p class="lede">Hwahae (화해) is the review app Koreans check before buying cosmetics. This site turns its public top-20 rankings into English every day: product names, ratings, review counts, prices and what reviewers praise, by category and by skin type.</p>
<p class="meta">Last ranking update: {esc(up)} KST</p>
<h2>Start here</h2><div class="grid">
<div class="card"><h3><a href="{BASE}guide/korean-skincare-routine/">Korean skincare routine</a></h3><p class="meta">The 5 steps in order, with Korea's #1 pick for each.</p></div>
<div class="card"><h3><a href="{BASE}guide/korean-sunscreen/">Best Korean sunscreen</a></h3><p class="meta">SPF50+ PA++++, mineral or chemical, and today's top 5.</p></div>
<div class="card"><h3><a href="{BASE}guide/korean-skincare-on-amazon/">Korean skincare on Amazon</a></h3><p class="meta">Korea's top-rated picks per step, linked to Amazon.</p></div>
<div class="card"><h3><a href="{BASE}brand/">Best by brand</a></h3><p class="meta">Torriden, Round Lab, Anua and more, ranked by Korean reviewers.</p></div>
<div class="card"><h3><a href="{BASE}trending/">Trending in Korea</a></h3><p class="meta">What is climbing fastest on Hwahae today.</p></div>
<div class="card"><h3><a href="{BASE}guide/">Guides by skin type</a></h3><p class="meta">Dry, oily, combination, sensitive and acne-prone skin.</p></div></div>
<h2>By category</h2><div class="grid">{''.join(c for c, rk in zip(cards, data['rankings']) if rk['type'] == 'category')}</div>
<h2>By skin type</h2><div class="grid">{''.join(c for c, rk in zip(cards, data['rankings']) if rk['type'] == 'skin')}</div>"""
    return page('K-Beauty Now: Korea\'s Top-Rated Skincare and Makeup, Updated Daily',
                'Hwahae\'s Korean cosmetics rankings in English, updated daily: top 20 skincare, sunscreen, serum, toner, cushion and more, plus picks by skin type.',
                '', body, up)


def threads_posts(data):
    """Daily text posts for Threads (one per category, rotating), saved to data/threads.json."""
    import datetime
    up = data['updatedAt'][:10]
    cats = [rk for rk in data['rankings'] if rk['type'] == 'category' and rk['slug'] not in ('all', 'skincare')]
    day = datetime.date.fromisoformat(up).toordinal()
    posts = []
    for k in range(3):
        rk = cats[(day * 3 + k) % len(cats)]
        noun = CAT[rk['slug']][1].replace('Korean ', '')
        rows = rk['rows']
        r = rows[0]
        t = ', '.join(x.lower() for x in r['topics'][:3])
        nm = lambda o: f"{brand_label(o).split(' (')[0]} {name_label(o).split(' SPF')[0].split(' (')[0]}"
        text = (f"Korea's #1 {({'serums and essences': 'serum'}.get(noun) or noun.rstrip('s'))} right now, by Korean reviewers on Hwahae (the review app Koreans check before buying):\n\n"
                f"1. {nm(r)}: {r['rating']:.2f} from {r['reviews']:,} reviews" + (f". Most-mentioned: {t}" if t else '') + "\n"
                + ''.join(f"{i}. {nm(o)}\n" for i, o in enumerate(rows[1:3], 2)) +
                f"\nFull top 20 and where to buy: {BASE}c/{rk['slug']}/\n\nAuto-translated from Hwahae every morning (AI-assisted, not sponsored).")
        text = re.sub(r'\b([A-Za-z])\.([A-Za-z]{2,})', r'\1. \2', text)  # 'S.NATURE' would be auto-linked as a domain
        if len(text) > 495:  # Threads limit is 500 characters
            text = re.sub(r'\. Most-mentioned: [^\n]*', '', text, count=1)
        if len(text) > 495:
            text = text.replace(' (the review app Koreans check before buying)', '')
        text = text[:500]
        posts.append({'category': rk['slug'], 'topic': 'K Beauty', 'text': text})
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'threads.json')
    json.dump({'date': up, 'posts': posts}, open(path, 'w'), ensure_ascii=False, indent=1)


def main():
    data = json.load(open(os.path.join(os.path.dirname(__file__), 'data', 'latest.json')))
    os.makedirs(OUT, exist_ok=True)
    urls = [BASE]
    for rk in data['rankings']:
        path, h = ranking_page(rk, data['updatedAt'])
        os.makedirs(f'{OUT}/{path}', exist_ok=True)
        open(f'{OUT}/{path}index.html', 'w').write(h)
        urls.append(BASE + path)
    for path, h in list(product_pages(data).items()) + list(extra_pages(data).items()):
        os.makedirs(f'{OUT}/{path}', exist_ok=True)
        open(f'{OUT}/{path}index.html', 'w').write(h)
        urls.append(BASE + path)
    open(f'{OUT}/index.html', 'w').write(index_page(data))
    open(f'{OUT}/rss.xml', 'w').write(pins_and_rss(data))
    threads_posts(data)
    day = data['fetchedAt'][:10]
    open(f'{OUT}/sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                          + ''.join(f'<url><loc>{u}</loc><lastmod>{day}</lastmod></url>' for u in urls) + '</urlset>')
    open(f'{OUT}/robots.txt', 'w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
    open(f'{OUT}/.nojekyll', 'w').write('')
    missing = sorted({r['name'] for rk in data['rankings'] for r in rk['rows'] if r['name'] not in N})
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'untranslated.txt'), 'w').write('\n'.join(missing))
    print(len(urls), 'pages;', len(missing), 'untranslated')


if __name__ == '__main__':
    main()
