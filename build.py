"""Build the K-beauty rankings site from data/latest.json (Hwahae public ranking pages)."""
import html, json, os, re, sys, urllib.parse
from names_en import N
BRANDS = json.load(open(os.path.join(os.path.dirname(__file__), 'brands_en.json')))

BASE = os.environ.get('SITE_BASE', 'https://koreanbeautynow.com/')
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
# Home "came from a video?" chips (label, path, highlighted). Same labels as TAP in ops/shorts.mjs.
JUMP = [("Korea's #1s on Amazon", 'guide/korean-skincare-on-amazon/', True), ('Full routine', 'guide/korean-skincare-routine/', True),
        ('Sunscreen', 'c/sunscreen/', False), ('Toner', 'c/toner/', False), ('Serum', 'c/serum/', False), ('Moisturizer', 'c/cream/', False),
        ('Cleanser', 'c/cleansing/', False), ('Masks', 'c/masks/', False), ('Cushion', 'c/cushion/', False), ('Lip', 'c/lip/', False),
        ('By concern', 'concern/', False), ('Top 20', 'c/all/', False)]

CSS = """.jump{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 10px}.jump a{border:1px solid var(--accent);border-radius:99px;padding:6px 13px;font-size:14px;font-weight:600;text-decoration:none;background:var(--card)}.jump a.hot{background:var(--accent);color:var(--card)}
#iab{display:none;background:var(--soft);border-radius:8px;padding:8px 12px;font-size:13.5px;margin:0 0 12px}
.cbw{margin-top:10px}.buy.cb{display:block;text-align:center;padding:11px 14px;margin:0 0 6px}.cbw .alt{font-size:13px;color:#6b665f}.cbw .alt a{color:#6b665f}.disc{font-size:13px;color:#6b665f;margin:0 0 14px}
ol.shop{padding-left:22px}ol.shop li{margin:10px 0}
table.cmp{border-collapse:collapse;width:100%;table-layout:fixed;margin:12px 0;font-size:14px;overflow-wrap:anywhere}table.cmp th,table.cmp td{border-bottom:1px solid #eadfd6;padding:9px 8px;text-align:left;vertical-align:top}table.cmp tr:first-child th{font-size:16px}table.cmp th:first-child{color:#6b665f;font-weight:600;width:28%}

:root{--ink:#22201d;--muted:#6b665f;--line:#e6e1da;--bg:#fbf8f4;--card:#fff;--accent:#b04a5a;--soft:#f4ede6}
@media (prefers-color-scheme:dark){:root{--ink:#ece7e1;--muted:#a9a29a;--line:#36312c;--bg:#171513;--card:#201d1a;--accent:#e58a98;--soft:#2a2521}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans KR",sans-serif}
main{max-width:880px;margin:0 auto;padding:28px 16px 72px}
header.top{border-bottom:1px solid var(--line);background:var(--card)}
header.top div{max-width:880px;margin:0 auto;padding:12px 16px;display:flex;gap:14px;flex-wrap:wrap;font-size:14px}
header.top a{color:var(--ink);text-decoration:none}header.top a.home{font-weight:700;margin-right:auto}
@media(max-width:640px){header.top div{gap:8px 14px;font-size:14px}header.top a.home{flex-basis:100%;margin-right:0}}
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
    n = N.get(r['name']) or r['name']
    return re.sub(r'\s*[\[(][^\])]*[가-힣][^\])]*[\])]\s*', ' ', n).strip() or n


def size_en(sz):
    """Hwahae size text in English: 24ml*10매 -> 24 ml x 10 sheets, 14g 2개입 -> 14 g, 2-pack, 본품15g+리필15g -> 15 g + 15 g refill."""
    s = re.split(r'\s*/', str(sz or ''))[0].strip()
    if re.search(r'fl\.?\s*oz', s, re.I) and re.search(r'[\d.]+\s*m[lL]', s):
        s = re.search(r'[\d.]+\s*m[lL]', s).group(0)
    s = re.sub(r'본품\s*', '', s)
    s = re.sub(r'\+\s*리필\s*([\d.]+\s*(?:ml|g|mL))', r' + \1 refill', s)
    s = re.sub(r'\*\s*(\d+)\s*매', r' x \1 sheets', s)
    s = re.sub(r'\s*\(?\s*(\d+)\s*매\s*\)?', r' (\1 sheets)', s)
    s = re.sub(r'\*\s*(\d+)\s*(?:개입|개|ea)', r' x \1', s, flags=re.I)
    s = re.sub(r'\s*(\d+)\s*개입', r', \1-pack', s)
    s = re.sub(r'(\d)(ml|mL|ML|g)\b', r'\1 \2', s).replace('mL', 'ml').replace('ML', 'ml')
    s = re.sub(r'[가-힣]+', '', s)
    s = re.sub(r'\(\s*[\d,\s]*\)', '', s).strip(' ,')
    return re.sub(r' x 1$', '', s)


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
LINK_NOTE = ('Most store links are search links. Some are affiliate links: we may earn a commission at no extra cost to you, and it never changes the ranking order.'
             if (any(AWIN_MID.values()) or AMAZON_TAG) else 'Store links are search links.')
if AMAZON_TAG:
    LINK_NOTE += ' As an Amazon Associate, K-Beauty Now earns from qualifying purchases.'


try:  # hand-checked product pages on Amazon US (brand + product name match); everything else stays a search link
    ASIN = json.load(open(os.path.join(_here, 'data', 'asin.json')))
except Exception:
    ASIN = {}


def amazon(q, pid=None):
    a = ASIN.get(str(pid)) if pid is not None else None
    if a:
        return f'https://www.amazon.com/dp/{a}?tag={AMAZON_TAG}'
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
        return (f'<p style="margin:12px 0 4px"><a class="buy" href="{esc(amazon(q, r.get("id")))}" rel="sponsored nofollow">Check price on Amazon</a></p>'
                '<p class="meta" style="margin:0">Affiliate link: as an Amazon Associate we earn from qualifying purchases.</p>')
    url, rel = awin('https://www.yesstyle.com/en/list.html?q=' + urllib.parse.quote(q), 'yesstyle')
    return f'<p style="margin:12px 0 4px"><a class="buy" href="{esc(url)}" rel="{rel}">Check price on YesStyle</a></p>'


def search_links(r, amazon_link=True):
    q = f"{brand_label(r).split(' (')[0]} {name_label(r).split(' SPF')[0].split(' (')[0]}"
    oy = 'https://global.oliveyoung.com/display/search?query=' + urllib.parse.quote(q)
    ys, ys_rel = awin('https://www.yesstyle.com/en/list.html?q=' + urllib.parse.quote(q), 'yesstyle')
    amz = f'<a href="{esc(amazon(q, r.get("id")))}" rel="sponsored nofollow">Amazon</a>' if (AMAZON_TAG and amazon_link) else ''
    return f'{amz}<a href="{oy}" rel="nofollow">Olive Young Global</a><a href="{esc(ys)}" rel="{ys_rel}">YesStyle</a><a href="{esc(r["url"])}" rel="nofollow">Hwahae page (KR)</a>'


def delta(r):
    if r['isNew']:
        return 'new'
    d = r['delta']
    if not d:
        return '–'
    return f'▲{d}' if d > 0 else f'▼{-d}'


def card_buy(r):
    """Primary Amazon button on list cards, store search links as small secondary links."""
    q = f"{brand_label(r).split(' (')[0]} {name_label(r).split(' SPF')[0].split(' (')[0]}"
    oy = 'https://global.oliveyoung.com/display/search?query=' + urllib.parse.quote(q)
    ys, ys_rel = awin('https://www.yesstyle.com/en/list.html?q=' + urllib.parse.quote(q), 'yesstyle')
    btn = f'<a class="buy cb" href="{esc(amazon(q, r.get("id")))}" rel="sponsored nofollow">Check price on Amazon</a>' if AMAZON_TAG else ''
    return (f'<div class="cbw">{btn}<span class="alt">or search <a href="{oy}" rel="nofollow">Olive&nbsp;Young&nbsp;Global</a> · '
            f'<a href="{esc(ys)}" rel="{ys_rel}">YesStyle</a></span></div>')


def row_html(r):
    price = f"Korea store price ₩{r['priceKrw']:,} ({usd(r['priceKrw'])})" if r['priceKrw'] else ''
    tags = ''.join(f'<span>{esc(t)}</span>' for t in r['topics'])
    ko = '' if name_label(r) == r['name'] else f'<div class="ko">{esc(r["brand"])} {esc(r["name"])}</div>'
    return f"""<li><div><div class="n">{r['rank']}</div><div class="d">{delta(r)}</div></div>
<div><div class="pn"><a href="{BASE}p/{r['id']}/" style="color:inherit;text-decoration:none">{esc(brand_label(r))} · {esc(name_label(r))}</a></div>{ko}
<div class="facts">{(f'{len(hist_load()[str(r["id"])]["dates"])} days in a top 20 · ') if len(hist_load().get(str(r['id']), {}).get('dates', ())) >= 2 else ''}★ {r['rating']:.2f} · {r['reviews']:,} reviews{(' · ' + esc(size_en(r['size']))) if r['size'] else ''}{(' · ' + price) if price else ''}</div>
<div class="tags">{tags}</div>{card_buy(r)}</div></li>"""


def default_img(path, updated):
    slug = path.strip('/').split('/')[-1]
    if path.startswith('guide/') and slug in GUIDE_PINS:
        return f'guide-{slug}-{updated[:7]}.jpg'
    return f'category-all-{updated[:10]}.jpg'


# Cloudflare Web Analytics (cookieless page views; the token is public by design)
CF_BEACON = '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{"token": "b4b5c7d729cd4dae931d4d02279c251d"}\'></script>'
# In-app browsers (Instagram, TikTok, Facebook, Threads) are not signed in to Amazon, so a visitor from a reel lands on
# Amazon logged out and rarely buys there. Show a one-line tip to those visitors only, and only on pages with an Amazon link.
IAB_JS = ('<script>try{if(/Instagram|FBAN|FBAV|musical_ly|BytedanceWebview|TikTok|Barcelona/i.test(navigator.userAgent)'
          '&&document.querySelector(\'a[href*="amazon.com"]\'))document.getElementById("iab").style.display="block"}catch(e){}</script>')
WEEK_CARD = ['']  # filled by week_page() once 7 days of history exist
NOINDEX = set()  # thin pages: reachable by link, kept out of search and the sitemap


def page(title, desc, path, body, updated, head=''):
    url = BASE + path
    if re.match(r'guide/skincare-for-.+-skin/$', path):  # same ranking as skin/<type>/ (audit 2026-10-30)
        NOINDEX.add(path)
    if path.startswith('brand/'):  # templated; reopen once each carries rank history (see audit 2026-10-29)
        NOINDEX.add(path)
    if path in NOINDEX:
        head = '<meta name="robots" content="noindex,follow">' + head
    nav = ''.join(f'<a href="{BASE}c/{s}/">{v[0]}</a>' for s, v in CAT.items() if s in ('skincare', 'sunscreen', 'serum', 'toner', 'cushion'))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="google-site-verification" content="0oISjJafxIxC-LdVeihPqTQ3o9DoxV5FSNgvVZB-tps">
<meta name="p:domain_verify" content="62fc4bdb9182a51a7a89f9e270417f58"/>
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:type" content="article"><meta property="og:site_name" content="K-Beauty Now">
<meta property="article:modified_time" content="{esc(updated[:10])}"><meta property="article:author" content="K-Beauty Now">{head or f'<meta property="og:image" content="{BASE}pins/{default_img(path, updated)}">'}
<style>{CSS}</style></head><body>
<header class="top"><div><a class="home" href="{BASE}">K-Beauty Now</a>{nav}<a href="{BASE}trending/">Trending</a><a href="{BASE}brand/">Brands</a><a href="{BASE}concern/">Concerns</a><a href="{BASE}guide/">Guides</a><a href="{BASE}about/">About</a></div></header>
<main><p class="disc">Some store links on this site are affiliate links (Amazon and others): we may earn a commission at no cost to you. It never changes the order, which is Hwahae's.</p><p id="iab">In Instagram or TikTok? Tap ··· → "Open in browser" first, so Amazon opens signed in.</p>{body}
<footer>Rankings come from the public ranking pages of Hwahae (화해), Korea's largest cosmetics review app, and are checked every day; pages change as soon as Hwahae refreshes its rankings. Hwahae ranking dated {esc(updated)} KST.
Pages are built automatically every day from Hwahae data; product names are translated by K-Beauty Now with AI assistance and checked against official brand names where we can verify them; brand names marked with Korean in brackets are transliterations, not official English names. Prices are Hwahae list prices in Korea; USD is approximate at {KRW_PER_USD:,} KRW per USD.
<a href="{BASE}privacy/">Privacy</a> · {LINK_NOTE} K-Beauty Now is independent and is not run by Hwahae, Olive Young or YesStyle.
<br>Daily top 5s: <a href="https://www.instagram.com/koreanbeautynow/" rel="me">Instagram</a> · <a href="https://www.threads.com/@koreanbeautynow" rel="me">Threads</a> · <a href="https://www.pinterest.com/whistlewhistle311kbeauty/" rel="me">Pinterest</a></footer></main>{IAB_JS}{CF_BEACON}</body></html>"""


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
        blurb = (f'Ranked using reviews from Hwahae users who registered {sk}. Many of the same products top every skin-type list, '
                 'so the useful signal is which ones rank higher or lower here than for other skin types.')
    body = f"""<p class="kicker">Hwahae ranking · updated {esc(updated[:10])}</p><h1>{esc(h1)}</h1>
<p class="lede">{esc(blurb)} Rank changes are Hwahae's own movement since the previous ranking. Tags are the review topics Korean users mention most.</p>
<ol class="rank">{rows}</ol>"""
    if rk['type'] == 'category' and rk['slug'] in COMPARE_CATS and len(rk['rows']) >= 3:
        cl = ''.join(f'<li><a href="{BASE}{compare_path(a, b)}">{esc(short_name(a))} vs {esc(short_name(b))}</a></li>' for a, b in top_pairs(rk['rows']))
        body += f'<h2>Top 3 head to head</h2><ul>{cl}</ul>'
        if rk['slug'] in VALUE_CATS:
            body += f'<p><a href="{BASE}value/{rk["slug"]}/">Best value by price per 100 ml</a></p>'
    ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': h1, 'itemListOrder': 'https://schema.org/ItemListOrderAscending',
          'numberOfItems': len(rk['rows']),
          'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f"{BASE}p/{r['id']}/", 'name': f"{brand_label(r)} {name_label(r)}"}
                              for i, r in enumerate(rk['rows'])]}
    img = f"{BASE}pins/{rk['type']}-{rk['slug']}-{updated[:10]}.jpg"
    head = (f'<meta property="og:image" content="{img}"><meta name="twitter:card" content="summary_large_image">'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")}</script>')
    return path, page(title, desc, path, body, updated, head)


def load_history():
    """Per product: dates seen in any Hwahae top 20, first date, best rank (label, rank). From data/YYYY-MM-DD.json."""
    import glob
    hist, days = {}, []
    for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', '20??-??-??.json'))):
        d = os.path.basename(f)[:10]
        try:
            snap = json.load(open(f))
        except Exception:
            continue
        days.append(d)
        for rk in snap['rankings']:
            label = CAT[rk['slug']][0] if rk['type'] == 'category' else f"Skincare for {SKIN[rk['slug']]}"
            for r in rk['rows']:
                h = hist.setdefault(str(r['id']), {'dates': set(), 'best': (label, 99)})
                h['dates'].add(d)
                if r['rank'] < h['best'][1]:
                    h['best'] = (label, r['rank'])
    return hist, days


HIST, HIST_DAYS = None, []


def hist_load():
    global HIST, HIST_DAYS
    if HIST is None:
        HIST, HIST_DAYS = load_history()
    return HIST


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
    hist_load()
    # head-to-head pages each product appears in (stored pairs plus today's top-3 pairs)
    try:
        cpairs = json.load(open(os.path.join(os.path.dirname(hist_path), 'compare_pairs.json')))
    except Exception:
        cpairs = {}
    for rk in data['rankings']:
        if rk['type'] == 'category' and rk['slug'] in COMPARE_CATS:
            for a, b in top_pairs(rk['rows']):
                cpairs.setdefault(compare_path(a, b), {'a': str(a['id']), 'b': str(b['id'])})
    vs = {}
    for path, q in cpairs.items():
        if q['a'] in hist and q['b'] in hist:
            vs.setdefault(q['a'], []).append((path, q['b']))
            vs.setdefault(q['b'], []).append((path, q['a']))
    pages = {}
    for pid, h in hist.items():
        r, current = h['r'], h['last'] == today
        hh = HIST.get(pid)
        if hh and len(HIST_DAYS) >= 14:
            seen = len(hh['dates'])
            first = min(hh['dates'])
            track = (f'<h2>Track record</h2><p>Tracked daily since {esc(HIST_DAYS[0])}. This product has been in a Hwahae top 20 on '
                     f'<strong>{seen} of {len(HIST_DAYS)}</strong> days tracked, first seen {esc(first)}. Best rank so far: '
                     f'<strong>#{hh["best"][1]}</strong> in {esc(hh["best"][0])}.</p>')
        else:
            seen, track = 0, ''
        if seen < 10:  # reopen to search only once the page carries real history
            NOINDEX.add(f"p/{pid}/")
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
        cmp_ = ''.join(f'<li><a href="{BASE}{path}">{esc(short_name(r))} vs {esc(short_name(hist[o]["r"]))}</a></li>' for path, o in vs.get(pid, []))
        near = (f'<h2>Compared head to head</h2><ul>{cmp_}</ul>' if cmp_ else '') + near
        cl = [f'<a href="{BASE}concern/{CONCERNS[t][0]}/">{esc(t.lower())}</a>' for t in r['topics'] if t in CONCERNS]
        clink = f'<p class="meta">Other products Korean reviewers call {" · ".join(cl)}</p>' if cl else ''
        bl = brand_label(r).split(' (')[0]
        bcount = sum(1 for x in hist.values() if brand_label(x['r']).split(' (')[0] == bl)
        blink = f'<p class="meta">More from this brand: <a href="{BASE}brand/{brand_slug(bl)}/">best {esc(bl)} products</a></p>' if bcount >= 2 else ''
        body = f"""<p class="kicker">Hwahae ranking profile</p><h1>{esc(nm)}</h1>
<p class="ko">{esc(r['brand'])} {esc(r['name'])}</p>
<div class="card"><div class="facts">★ <strong>{r['rating']:.2f}</strong> on Hwahae from {r['reviews']:,} Korean reviews</div>
<div class="facts">Korean list price: {price}{(' · ' + esc(r['size'])) if r['size'] else ''}</div>
<div class="tags">{tags}</div>{buy_button(r)}<div class="links">{search_links(r, amazon_link=False)}</div></div>
{praise}{status}{track}{near}{blink}{clink}
<h2>Buying it outside Korea</h2><p>Hwahae prices are Korean list prices; international shops usually charge more after shipping. Check the size matches ({esc(r['size']) if r['size'] else 'sizes vary by market'}) and buy from authorised sellers to avoid fakes.</p>
<p class="meta">Tags are the review topics Korean Hwahae users mention most for this product. Ratings and ranks change daily.</p>"""
        title = f"{nm}: Hwahae Rating {r['rating']:.2f} and Korea Ranking"
        desc = f"{nm} is rated {r['rating']:.2f} from {r['reviews']:,} Korean reviews on Hwahae. See where it ranks in Korea, its Korean price and what reviewers praise."
        pages[f"p/{pid}/"] = page(title, desc, f"p/{pid}/", body, data['updatedAt'])
    pages.update(brand_pages(hist, today, data['updatedAt']))
    pages.update(concern_pages(hist, today, data['updatedAt']))
    pages.update(ingredient_pages(hist, today, data['updatedAt']))
    pages.update(week_page(data))
    return pages


CONCERNS = {  # review topic -> (slug, h1, lede)
    'Moisturizing': ('moisturizing', 'The most moisturizing Korean skincare, according to Korean reviewers', 'Products Korean Hwahae users most often describe as moisturizing.'),
    'Hydrating': ('hydrating', 'The most hydrating Korean skincare, according to Korean reviewers', 'Products Korean Hwahae users most often describe as hydrating.'),
    'Fixes inner dryness': ('dehydrated-skin', 'Korean skincare for dehydrated skin: what Korean reviewers say fixes inner dryness', 'Korean reviewers use the phrase "속건조 해결" (fixes inner dryness) for skin that feels tight underneath even when the surface is oily. These products get that comment most.'),
    'Lightweight': ('lightweight', 'Lightweight Korean skincare Korean reviewers love', 'Products Korean Hwahae users most often call lightweight.'),
    'Non-sticky': ('non-sticky', 'Non-sticky Korean skincare, according to Korean reviewers', 'Products Korean Hwahae users most often describe as non-sticky, a top request in humid weather.'),
    'Non-irritating': ('non-irritating', 'Non-irritating Korean skincare for sensitive skin', 'Products Korean Hwahae users most often describe as non-irritating.'),
    'Soothing': ('soothing', 'The most soothing Korean skincare for redness, according to Korean reviewers', 'Products Korean Hwahae users most often describe as soothing.'),
    'No breakouts': ('no-breakouts', "Korean skincare that doesn't cause breakouts, according to Korean reviewers", 'Products Korean Hwahae users most often say did not break them out.'),
    'Clears breakouts': ('breakouts', 'Korean picks for blemish-prone skin, by what Korean reviewers mention', 'Products Hwahae users with blemish-prone skin mention most for breakouts. Reviews are personal experience, not medical claims; see a dermatologist for acne.'),
    'Pore care': ('pores', 'Korean skincare for pores, according to Korean reviewers', 'Products Korean Hwahae users most often mention for pore care.'),
    'Oil-free feel': ('oil-free', 'Oil-free feel Korean skincare for oily skin', 'Products Korean Hwahae users most often say feel oil-free.'),
    'Glowy': ('glowy', 'Glowy Korean skincare and makeup, according to Korean reviewers', 'Products Korean Hwahae users most often describe as glowy.'),
    'Exfoliates well': ('exfoliating', 'Gentle exfoliating Korean skincare Korean reviewers rate highest', 'Products Korean Hwahae users most often say exfoliate well.'),
    'Long-lasting': ('long-lasting', 'Long-lasting Korean makeup, according to Korean reviewers', 'Products Korean Hwahae users most often describe as long-lasting.'),
}


INGREDIENTS = {  # slug: (label, name regex, what it is)
    'hyaluronic-acid': ('Hyaluronic acid', r'hyalu', 'Hyaluronic acid is a humectant: it holds water in the top layer of the skin. Korean toners, serums and creams often combine several molecule sizes, which is why many product names say "low molecular".'),
    'ceramide': ('Ceramide', r'ceramide|\bcera\b', 'Ceramides are lipids that occur naturally in the skin barrier. Creams and lotions with ceramides are a common pick in Korea for dry, tight or easily irritated skin, especially in winter.'),
    'centella-cica': ('Centella (cica)', r'cica|centella|madecass', 'Centella asiatica, sold in Korea as "cica", and its compounds such as madecassoside are used in calming products for red or irritated skin.'),
    'pdrn': ('PDRN', r'pdrn', 'PDRN (polydeoxyribonucleotide) is made from DNA fragments, often from salmon. It became one of the biggest K-beauty trends of 2025 and 2026, marketed for repair and firmness; evidence for skincare use is still limited, so treat it as a hydrating ingredient first.'),
    'heartleaf': ('Heartleaf', r'heartleaf', 'Heartleaf (Houttuynia cordata, 어성초) extract is a Korean favourite in soothing toners and pads, often picked for oily and blemish-prone skin.'),
    'panthenol': ('Panthenol', r'panthenol', 'Panthenol (provitamin B5) attracts water and is used in soothing and barrier products.'),
    'niacinamide': ('Niacinamide', r'niacinamide', 'Niacinamide (vitamin B3) is used for uneven tone, oiliness and the look of pores.'),
    'squalane': ('Squalane', r'squalane', 'Squalane is a light, stable oil that softens the skin without feeling heavy.'),
}


def ingredient_pages(hist, today, updated):
    """Ingredient pages only exist once at least 8 ranked products contain the ingredient (no thin pages)."""
    pages, idx = {}, []
    for slug, (label, rx, what) in INGREDIENTS.items():
        items = [(pid, h) for pid, h in hist.items() if re.search(rx, name_label(h['r']), re.I)]
        if len(items) < 8:
            continue
        items.sort(key=lambda t: (t[1]['last'] != today, min(x[2] for x in t[1]['ranks']), -t[1]['r']['reviews']))
        cards = []
        for pid, h in items[:20]:
            r = h['r']
            b = brand_label(r).split(' (')[0]
            best = min(h['ranks'], key=lambda x: x[2])
            q = f"{b} {name_label(r).split(' SPF')[0].split(' (')[0]}"
            amz = f'<a class="buy" href="{esc(amazon(q, r["id"]))}" rel="sponsored nofollow">See it on Amazon</a>' if AMAZON_TAG else ''
            tags = ', '.join(t.lower() for t in r['topics'][:3])
            now = '' if h['last'] == today else f' (last seen {esc(h["last"])})'
            cards.append(f'<div class="card"><p class="kicker">#{best[2]} in <a href="{best[1]}">{esc(best[0])}</a>{now}</p>'
                         f'<h3><a href="{BASE}p/{pid}/">{esc(b)} {esc(name_label(r))}</a></h3>'
                         f'<p class="meta">★ {r["rating"]:.2f} from {r["reviews"]:,} Korean reviews' + (f'. Reviewers mention: {esc(tags)}.' if tags else '.') + f'</p><p>{amz}</p></div>')
        h1 = f'Best Korean {label.lower()} skincare, ranked by Korean reviewers'
        body = (f'<p class="kicker">By ingredient · updated {esc(updated[:10])}</p><h1>{esc(h1)}</h1>'
                f'<p class="lede">{esc(what)}</p>'
                f'<p>Below: every product with {esc(label.lower())} in its name that has made a Hwahae top 20 since we started tracking, '
                'products in today\'s rankings first, then by best rank. Hwahae is Korea\'s biggest cosmetics review app.</p>'
                f'<div class="grid">{"".join(cards)}</div><p class="meta">We list products by name; check the full ingredient list on the package or shop page. {esc(LINK_NOTE)}</p>'
                f'<p><a href="{BASE}ingredient/">All ingredients</a> · <a href="{BASE}concern/">By concern</a> · <a href="{BASE}guide/">Buying guides</a></p>')
        pages[f'ingredient/{slug}/'] = page(f'Best Korean {label} Skincare: Ranked by Korean Reviewers (Hwahae)',
                                           f'{len(items)} Korean {label.lower()} products that made a Hwahae top 20, with ratings, review counts and where to buy.',
                                           f'ingredient/{slug}/', body, updated)
        idx.append((slug, label, len(items)))
    if idx:
        lst = ''.join(f'<div class="card"><h3><a href="{BASE}ingredient/{sl}/">{esc(lb)}</a></h3><p class="meta">{n} ranked products</p></div>' for sl, lb, n in idx)
        pages['ingredient/'] = page('Korean Skincare by Ingredient: Ranked by Korean Reviewers',
                                    'Korean skincare grouped by key ingredient (hyaluronic acid, ceramide, cica and more), ranked from Hwahae.',
                                    'ingredient/', f'<p class="kicker">By ingredient</p><h1>Korean skincare by ingredient</h1><p class="lede">Products that made a Hwahae top 20, grouped by the key ingredient in their name. A page appears once at least 8 ranked products share an ingredient.</p>'
                                    f'<p>A word of caution: we match on the product name, so a product called "ceramide cream" is listed even if the ceramide content is small, '
                                    f'and products that contain an ingredient without naming it are missed. Use these pages to find candidates, then read the full ingredient list on the package.</p><div class="grid">{lst}</div>', updated)
    return pages


def concern_pages(hist, today, updated):
    pages, idx = {}, []
    for topic, (slug, h1, lede) in CONCERNS.items():
        items = [(pid, h) for pid, h in hist.items() if topic in h['r']['topics']]
        if len(items) < 4:
            continue
        if len(items) < 8:
            NOINDEX.add(f'concern/{slug}/')
        items.sort(key=lambda t: (t[1]['last'] != today, t[1]['r']['topics'].index(topic), -t[1]['r']['rating'] * min(t[1]['r']['reviews'], 20000)))
        cards = []
        for pid, h in items[:20]:
            r = h['r']
            b = brand_label(r).split(' (')[0]
            best = min(h['ranks'], key=lambda x: x[2])
            q = f"{b} {name_label(r).split(' SPF')[0].split(' (')[0]}"
            amz = f'<a class="buy" href="{esc(amazon(q, r["id"]))}" rel="sponsored nofollow">See it on Amazon</a>' if AMAZON_TAG else ''
            pos = r['topics'].index(topic) + 1
            cards.append(f'<div class="card"><p class="kicker">#{best[2]} in <a href="{best[1]}">{esc(best[0])}</a></p>'
                         f'<h3><a href="{BASE}p/{pid}/">{esc(b)} {esc(name_label(r))}</a></h3>'
                         f'<p class="meta">★ {r["rating"]:.2f} from {r["reviews"]:,} Korean reviews. "{esc(topic)}" is the {["", "most", "second most", "third most"][min(pos, 3)] or "a"} mentioned review topic.</p><p>{amz}</p></div>')
        body = (f'<p class="kicker">By concern · updated {esc(updated[:10])}</p><h1>{esc(h1)}</h1><p class="lede">{esc(lede)} '
                'Hwahae, Korea\'s biggest cosmetics review app, groups its reviews into topics; this list shows ranked products where this topic is among the top three, strongest first.</p>'
                f'<div class="grid">{"".join(cards)}</div><p class="meta">{esc(LINK_NOTE)}</p>'
                f'<p><a href="{BASE}concern/">All concerns</a> · <a href="{BASE}guide/">Buying guides</a></p>')
        title = h1.replace('according to Korean reviewers', 'Ranked by Korean Reviewers').strip()
        title = title[0].upper() + title[1:] + ' (Hwahae)'
        pages[f'concern/{slug}/'] = page(title, f'{lede} {len(items)} Korean products, with ratings, review counts and where to buy.', f'concern/{slug}/', body, updated)
        idx.append((slug, h1, len(items)))
    lst = ''.join(f'<div class="card"><h3><a href="{BASE}concern/{sl}/">{esc(h1.split(",")[0].split(":")[0])}</a></h3><p class="meta">{n} products</p></div>' for sl, h1, n in idx)
    pages['concern/'] = page('Korean Skincare by Concern: What Korean Reviewers Say Works',
                             'Korean skincare grouped by what Korean reviewers actually say about it: moisturizing, non-sticky, soothing, no breakouts, pores and more.',
                             'concern/', f'<p class="kicker">By concern</p><h1>Korean skincare by concern</h1><p class="lede">Grouped by the review topics Korean Hwahae users mention most.</p>'
                             f'<p>Hwahae tags each product with what its reviewers bring up most often, such as "non-sticky" or "fixes inner dryness". '
                             f'These pages collect the ranked products where that topic comes up near the top. They reflect how Korean users describe their own experience, '
                             f'not tested results or medical claims, so treat them as a shortlist and check how your own skin reacts.</p><div class="grid">{lst}</div>', updated)
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
        if len(items) < 4:
            NOINDEX.add(f'brand/{slug}/')
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
            amz = f'<a class="buy" href="{esc(amazon(q, r["id"]))}" rel="sponsored nofollow">See it on Amazon</a>' if AMAZON_TAG else ''
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
        pages[f'brand/{slug}/'] = page(f'Best {b} Products: Ranked by Korean Reviewers on Hwahae',
                                       f'The {b} ({ko}) products Korean reviewers rank highest on Hwahae, with ratings, review counts and what they praise. Checked daily against Hwahae.',
                                       f'brand/{slug}/', body, updated, head)
        idx.append((b, slug, len(items), live))
    lst = ''.join(f'<div class="card"><h3><a href="{BASE}brand/{sl}/">{esc(b)}</a></h3><p class="meta">{n} ranked products, {lv} in today\'s top 20s</p></div>' for b, sl, n, lv in idx)
    pages['brand/'] = page('Korean Skincare Brands Ranked by Korean Reviewers (Hwahae)',
                           'Every Korean beauty brand with several products in Hwahae\'s top 20 rankings, with their best-rated products. Checked daily against Hwahae.',
                           'brand/', f'<p class="kicker">Brands</p><h1>Korean beauty brands Korean reviewers rank highest</h1><p class="lede">Brands with two or more products in a Hwahae top 20. Click a brand for its best-ranked products.</p><div class="grid">{lst}</div>', updated)
    return pages


GUIDES = {
    'korean-toner': ('toner', 'Best Korean Toner: What Koreans Pick on Hwahae',
        'Toner, toner pad or essence toner? How Korean toners work and the 5 toners Korean Hwahae users rank highest today.',
        'Best Korean toner: what Koreans pick, and how to choose',
        'In Korea a toner is not an astringent: it is the first hydrating step after cleansing. Here is how to pick one, and the five toners Korean Hwahae users rank highest today.',
        '<h2>Three kinds of Korean toner</h2><ul><li><b>Hydrating toner</b> (스킨/토너): watery, applied with hands or a cotton pad right after cleansing.</li>'
        '<li><b>Toner pad</b> (토너패드): pre-soaked pads, often with mild exfoliating acids (PHA, LHA) or soothing extracts. Good for a quick routine.</li>'
        '<li><b>Essence toner</b>: thicker, sits between toner and serum. Useful for dry skin.</li></ul>'
        '<h2>How to choose</h2><p>Dry skin: look for glycerin, panthenol or hyaluronic acid. Oily or acne-prone skin: lighter toners or pads with PHA/BHA, used a few times a week. Sensitive skin: short ingredient lists, mugwort (쑥) or centella (병풀). Check the review tags under each product: Korean users often mention Soothing, Moisturizing or Non-sticky.</p>'),
    'korean-serum': ('serum', 'Best Korean Serum and Ampoule: Hwahae Top Picks',
        'Serum, essence or ampoule? What the Korean terms mean and the 5 serums Korean Hwahae users rank highest today.',
        'Best Korean serum: what Koreans pick, and how to choose',
        'Korean brands use serum, essence and ampoule for similar products. Here is what the words usually mean, and the five serums Korean Hwahae users rank highest today.',
        '<h2>Serum, essence, ampoule</h2><p>There is no legal difference. In practice an <b>essence</b> is lighter, a <b>serum</b> is a little thicker, and an <b>ampoule</b> is marketed as the most concentrated. Choose by the active ingredient, not the word.</p>'
        '<h2>Common Korean serum ingredients</h2><ul><li>Niacinamide: tone and oil control.</li><li>Vitamin C: brightening; can sting sensitive skin.</li><li>Centella, mugwort, heartleaf (어성초): soothing.</li><li>Retinal or retinol: anti-ageing; use at night and wear sunscreen by day.</li><li>Hyaluronic acid, panthenol: hydration.</li></ul>'),
    'korean-moisturizer': ('cream', 'Best Korean Moisturizer: Hwahae Top Creams',
        'How to choose a Korean cream for dry, oily or sensitive skin, and the 5 creams Korean Hwahae users rank highest today.',
        'Best Korean moisturizer: what Koreans pick, and how to choose',
        'The cream is the step that seals in the toner and serum. Here is how to choose by skin type, and the five creams Korean Hwahae users rank highest today.',
        '<h2>Choose by texture</h2><ul><li><b>Gel cream</b>: light, good for oily skin and hot weather.</li><li><b>Barrier cream</b> with ceramides: for dry or irritated skin, and for winter.</li><li><b>Soothing cream</b> with centella or panthenol: for redness and sensitive skin.</li></ul>'
        '<p>For skin-type rankings, see <a href="https://koreanbeautynow.com/skin/dry/">dry skin</a>, <a href="https://koreanbeautynow.com/skin/oily/">oily skin</a> and <a href="https://koreanbeautynow.com/skin/sensitive/">sensitive skin</a>.</p>'),
    'korean-cleanser': ('cleansing', 'Best Korean Cleanser: Double Cleansing Picks from Hwahae',
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
    'korean-skincare-on-amazon': ('cream', 'Best Korean skincare on Amazon, picked by Korean reviewers', ['Start from what Koreans rate highest.', 'Buy from the brand store or Ships from Amazon.', 'Two top picks per routine step.', 'Checked daily against Hwahae.']),
    'korean-cleanser': ('cleansing', 'Korean double cleansing in 2 steps', ['1. Oil or balm on dry skin, then rinse.', '2. Foam or gel cleanser.', 'Morning: one gentle cleanser is enough.', 'Tight after washing? Try a low-pH foam.']),
}

for _k, _t, _need, _avoid, _key in [
    ('dry', 'dry skin', 'Layer hydration: a hydrating toner (patted in two or three times), a serum with hyaluronic acid or panthenol, then a ceramide cream. Look for the review tags Moisturizing and Fixes inner dryness.', 'Foaming cleansers that leave skin tight, and alcohol-heavy toners.', 'Ceramides, panthenol, glycerin, squalane'),
    ('oily', 'oily skin', 'Keep it light: a gel cleanser, a watery toner or a toner pad with PHA or BHA a few times a week, niacinamide serum and a gel cream. Oily skin still needs moisture, or it makes more oil.', 'Skipping moisturizer, and heavy balm cleansers left on the skin.', 'Niacinamide, BHA (salicylic acid), heartleaf, green tea'),
    ('combination', 'combination skin', 'Treat zones differently: a light gel cream all over and a richer cream only on dry cheeks. A gentle low-pH cleanser keeps both areas balanced.', 'Using strong oil-control products on dry areas.', 'Niacinamide, hyaluronic acid, panthenol'),
    ('sensitive', 'sensitive skin', 'Fewer products, shorter ingredient lists, patch test first. Korean brands make many soothing lines with centella (병풀) or mugwort (쑥). Mineral sunscreens (무기자차) are usually gentler.', 'Fragrance, essential oils, strong acids and high-dose vitamin C.', 'Centella, mugwort, panthenol, madecassoside'),
    ('acne-prone', 'acne-prone skin', 'Gentle cleansing twice a day, a BHA or heartleaf toner, and light non-comedogenic moisturizer. Do not skip sunscreen: it helps marks fade.', 'Over-washing, scrubs, and heavy oils on breakout areas.', 'BHA, heartleaf (어성초), tea tree, niacinamide, azelaic acid'),
]:
    GUIDES[f'skincare-for-{_k}-skin'] = (f'skin:{_k}', f'Best Korean Skincare for {_t.title()}: Hwahae Top Picks',
        f'How to build a Korean skincare routine for {_t}, which ingredients to look for, and the 5 products Hwahae users with {_t} rank highest today.',
        f'Korean skincare for {_t}: what works, and what Koreans pick',
        f'Hwahae lets users register their skin type, so its rankings show what people with {_t} actually rate highly. Here is how to build a routine for {_t}, and today\'s top 5.',
        f'<h2>How to build the routine</h2><p>{_need}</p><h2>Ingredients to look for</h2><p>{_key}.</p><h2>What to avoid</h2><p>{_avoid}</p>'
        f'<p>New to the order of steps? See the <a href="https://koreanbeautynow.com/guide/korean-skincare-routine/">Korean skincare routine guide</a>.</p>')


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


def week_page(data):
    """This week in Korea: compares today's Hwahae top 20s with the snapshot 7 days earlier (data/YYYY-MM-DD.json).
    Only built once 7 days of history exist, so it never shows made-up movement."""
    import datetime
    hist_load()
    today = data['updatedAt'][:10]
    want = (datetime.date.fromisoformat(today) - datetime.timedelta(days=7)).isoformat()
    older = [d for d in HIST_DAYS if d <= want]
    if not older:
        return {}
    then_day = older[-1]
    then = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', f'{then_day}.json')))
    window = [d for d in HIST_DAYS if then_day <= d <= today]
    prev = {(rk['type'], rk['slug']): {r['id']: r['rank'] for r in rk['rows']} for rk in then['rankings']}
    climbs, news, outs = [], [], []
    for rk in data['rankings']:
        if rk['type'] != 'category' or rk['slug'] in ('all', 'skincare'):
            continue
        p = prev.get(('category', rk['slug']), {})
        if not p:
            continue
        noun = CAT[rk['slug']][1]
        cur = {r['id'] for r in rk['rows']}
        for r in rk['rows']:
            if r['id'] in p and p[r['id']] - r['rank'] > 0:
                climbs.append((p[r['id']] - r['rank'], p[r['id']], r, noun, rk['slug']))
            elif r['id'] not in p:
                news.append((r['rank'], r, noun, rk['slug']))
        for t in then['rankings']:
            if t['type'] == 'category' and t['slug'] == rk['slug']:
                outs += [(o, noun) for o in t['rows'] if o['id'] not in cur and o['rank'] <= 10]
    steady = []
    for rk in data['rankings']:
        if rk['type'] == 'category' and rk['slug'] == 'all':
            for r in rk['rows']:
                n = len([d for d in hist_load().get(str(r['id']), {}).get('dates', ()) if d in window])
                if n == len(window):
                    steady.append(r)
    if not (climbs or news):
        return {}
    climbs.sort(key=lambda t: (-t[0], t[2]['rank']))
    news.sort(key=lambda t: t[0])

    def li(r, note):
        return (f'<li><a href="{BASE}p/{r["id"]}/">{esc(brand_label(r))} {esc(name_label(r))}</a> '
                f'<span class="meta">{note} · ★ {r["rating"]:.2f}, {r["reviews"]:,} reviews</span></li>')
    body = (f'<p class="kicker">This week · {esc(then_day)} to {esc(today)}</p><h1>This week in Korean skincare: what moved on Hwahae</h1>'
            f'<p class="lede">We save every Hwahae top 20 each morning. This page compares today with {(datetime.date.fromisoformat(today) - datetime.date.fromisoformat(then_day)).days} days ago, '
            'so you can see which products Korean users are moving up, and which ones just arrived.</p>')
    if climbs:
        body += '<h2>Biggest climbers</h2><ol>' + ''.join(
            li(r, f'#{was} → #{r["rank"]} in <a href="{BASE}c/{sl}/">{esc(noun)}</a>') for up, was, r, noun, sl in climbs[:10]) + '</ol>'
    if news:
        body += '<h2>New in a top 20 this week</h2><ol>' + ''.join(
            li(r, f'#{rank} in <a href="{BASE}c/{sl}/">{esc(noun)}</a>') for rank, r, noun, sl in news[:10]) + '</ol>'
    if steady:
        body += (f'<h2>Held the overall top 20 every day</h2><p>In the overall Hwahae ranking on all {len(window)} days we tracked:</p><ol>'
                 + ''.join(li(r, f'#{r["rank"]} today') for r in steady[:10]) + '</ol>')
    if outs:
        body += '<h2>Dropped out of a top 20</h2><p>Was top 10 a week ago, not in the top 20 today:</p><ul>' + ''.join(
            f'<li>{esc(brand_label(o))} {esc(name_label(o))} <span class="meta">(was #{o["rank"]} in {esc(noun)})</span></li>' for o, noun in outs[:8]) + '</ul>'
    body += f'<p class="meta">{esc(LINK_NOTE)}</p>'
    # Reddit draft for r/AsianBeauty-style weekly data posts: plain text, data first, one link at the end. Never posted automatically.
    md = [f"Title: What moved on Hwahae (Korea's biggest cosmetics review app) this week, {then_day} to {today}", '',
          "I track the public Hwahae top 20s every day. Here is what changed over the last week. Ratings and review counts are from Korean users.", '']
    if climbs:
        md += ['**Biggest climbers**', ''] + [f"- {brand_label(r).split(' (')[0]} {name_label(r)}: #{was} to #{r['rank']} in {noun} ({r['rating']:.2f}, {r['reviews']:,} reviews)"
                                            for up_, was, r, noun, sl in climbs[:7]] + ['']
    if news:
        md += ['**New in a top 20**', ''] + [f"- {brand_label(r).split(' (')[0]} {name_label(r)}: #{rank} in {noun}" for rank, r, noun, sl in news[:7]] + ['']
    if steady:
        md += [f'**In the overall top 20 every day ({len(window)} days)**', ''] + [f"- {brand_label(r).split(' (')[0]} {name_label(r)} (#{r['rank']} today)" for r in steady[:7]] + ['']
    md += ["Full daily lists (English names, Korean prices) if anyone wants them: " + BASE + "this-week/", '',
           "Disclosure: I run that site. It translates Hwahae's public rankings with AI help, and some shop links on it are affiliate links. "
           "Nothing here is sponsored and the ranking order is Hwahae's, not mine.", '',
           "<!-- Posting notes: r/AsianBeauty needs 20 comment karma on the sub, a 1:10 self-promo ratio, max 2 self-promo posts a week, "
           "the Original Content flair, and affiliate disclosure in the text. Do not post until the account genuinely meets that. -->"]
    try:
        open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'reddit_draft.md'), 'w').write('\n'.join(md))
    except Exception:
        pass
    WEEK_CARD[0] = (f'<div class="card"><h3><a href="{BASE}this-week/">This week in Korea</a></h3>'
                    '<p class="meta">Biggest climbers and new arrivals over the last 7 days.</p></div>')
    return {'this-week/': page(f'This Week in Korean Skincare: Biggest Movers on Hwahae ({today})',
                               'Which Korean skincare products climbed, arrived or held the Hwahae top 20 this week, from daily snapshots.',
                               'this-week/', body, data['updatedAt'])}


COMPARE_CATS = ('toner', 'serum', 'cream', 'cleansing', 'sunscreen', 'cushion', 'lip', 'masks')
VALUE_CATS = ('toner', 'serum', 'cream', 'cleansing', 'sunscreen')  # sold by volume, so price per 100 ml is fair


def size_ml(r):
    """Volume in ml (or g) from Hwahae's size text; None for multi-packs and sheet counts."""
    s = str(r.get('size') or '')
    if not s or re.search(r'[*+매개]|x\s*\d', s, re.I):
        return None
    m = re.search(r'(\d+(?:\.\d+)?)\s*(ml|g)\b', s, re.I)
    return float(m.group(1)) if m and float(m.group(1)) > 0 else None


def short_name(r):
    return f"{brand_label(r).split(' (')[0]} {name_label(r).split(' SPF')[0].split(' (')[0]}"


def product_slug(r):
    return '-'.join(brand_slug(short_name(r)).split('-')[:8])


def compare_path(a, b):
    return f"compare/{product_slug(a)}-vs-{product_slug(b)}/"


def top_pairs(rows):
    top = rows[:3]
    return [(top[i], top[j]) for i in range(len(top)) for j in range(i + 1, len(top))]


def per100(r):
    ml = size_ml(r)
    return r['priceKrw'] / ml * 100 if (ml and r.get('priceKrw')) else None


def compare_pages(data):
    """Head-to-head pages for the top 3 of each category (3 pairs each), plus price-per-100 ml value pages.
    Pairs are remembered in data/compare_pairs.json so a page stays up (with its last data) after the pair drops out."""
    base = os.path.dirname(os.path.abspath(__file__))
    ppath = os.path.join(base, 'data', 'compare_pairs.json')
    try:
        pairs = json.load(open(ppath))
    except Exception:
        pairs = {}
    hist = json.load(open(os.path.join(base, 'data', 'products.json')))
    up, today = data['updatedAt'], data['updatedAt'][:10]
    by = {rk['slug']: rk for rk in data['rankings'] if rk['type'] == 'category'}
    for slug in COMPARE_CATS:
        rk = by.get(slug)
        if not rk:
            continue
        for a, b in top_pairs(rk['rows']):
            path = compare_path(a, b)
            pairs.setdefault(path, {'a': str(a['id']), 'b': str(b['id']), 'cat': slug, 'since': today})
            pairs[path]['last'] = today
    json.dump(pairs, open(ppath, 'w'), indent=0, sort_keys=True)
    hl = hist_load()
    pages = {}
    for path, pr in pairs.items():
        ha, hb = hist.get(pr['a']), hist.get(pr['b'])
        if not ha or not hb:
            continue
        a, b = ha['r'], hb['r']
        cat = pr['cat']
        noun = CAT[cat][1]
        rows = by.get(cat, {}).get('rows', [])
        rank = {str(r['id']): r['rank'] for r in rows}
        na, nb = short_name(a), short_name(b)
        current = pr.get('last') == today
        days = lambda r: len(hl.get(str(r['id']), {}).get('dates', ()))

        def cell_rank(r):
            return f"#{rank[str(r['id'])]}" if str(r['id']) in rank else 'not in today\'s top 20'

        def money(r):
            return f"₩{r['priceKrw']:,} ({usd(r['priceKrw'])})" if r.get('priceKrw') else 'not listed'

        def p100(r):
            v = per100(r)
            return f"₩{v:,.0f} ({usd(v)})" if v else 'n/a'

        trs = [('Rank in ' + CAT[cat][0] + ' today', cell_rank(a), cell_rank(b)),
               ('Hwahae rating', f"★ {a['rating']:.2f}", f"★ {b['rating']:.2f}"),
               ('Korean reviews', f"{a['reviews']:,}", f"{b['reviews']:,}"),
               ('Korean list price', money(a), money(b)),
               ('Size', esc(str(a.get('size') or 'n/a')), esc(str(b.get('size') or 'n/a'))),
               ('Price per 100 ml', p100(a), p100(b)),
               *([('Days in a Hwahae top 20', str(days(a)), str(days(b)))] if min(days(a), days(b)) >= 7 else []),
               ('What reviewers mention most', esc(', '.join(t.lower() for t in a['topics']) or 'n/a'), esc(', '.join(t.lower() for t in b['topics']) or 'n/a'))]
        table = ('<div style="overflow-x:auto"><table class="cmp"><tr><th></th>'
                 f'<th><a href="{BASE}p/{pr["a"]}/">{esc(na)}</a></th><th><a href="{BASE}p/{pr["b"]}/">{esc(nb)}</a></th></tr>'
                 + ''.join(f'<tr><th>{esc(k)}</th><td>{x}</td><td>{y}</td></tr>' for k, x, y in trs) + '</table></div>')
        # plain-language read of the numbers
        pts = []
        dr = a['rating'] - b['rating']
        if abs(dr) < 0.05:
            pts.append(f"Ratings are practically tied ({a['rating']:.2f} vs {b['rating']:.2f}).")
        else:
            hi, lo = (na, nb) if dr > 0 else (nb, na)
            pts.append(f"{hi} is rated higher ({max(a['rating'], b['rating']):.2f} vs {min(a['rating'], b['rating']):.2f}).")
        if a['reviews'] and b['reviews']:
            big, small = (a, b) if a['reviews'] >= b['reviews'] else (b, a)
            ratio = big['reviews'] / max(small['reviews'], 1)
            if ratio >= 1.5:
                pts.append(f"{short_name(big)} has {ratio:.1f}x as many Korean reviews, so its rating rests on a bigger base.")
            else:
                pts.append('Both have a similar number of Korean reviews.')
        va, vb = per100(a), per100(b)
        if va and vb and abs(va - vb) / max(va, vb) >= 0.1:
            ch = (na, va, vb) if va < vb else (nb, vb, va)
            pts.append(f"{ch[0]} costs less per 100 ml in Korea (₩{ch[1]:,.0f} vs ₩{ch[2]:,.0f}).")
        elif va and vb:
            pts.append('Price per 100 ml is within 10% of each other.')
        ta, tb = set(a['topics']), set(b['topics'])
        both, only_a, only_b = ta & tb, [t for t in a['topics'] if t not in tb], [t for t in b['topics'] if t not in ta]
        pick = ''
        if only_a or only_b:
            pick = '<h2>Which one fits you</h2><ul>'
            if only_a:
                pick += f"<li><strong>{esc(na)}</strong> if you care most about: {esc(', '.join(t.lower() for t in only_a))}.</li>"
            if only_b:
                pick += f"<li><strong>{esc(nb)}</strong> if you care most about: {esc(', '.join(t.lower() for t in only_b))}.</li>"
            pick += '</ul>'
            if both:
                pick += f"<p>Korean reviewers praise both for: {esc(', '.join(t.lower() for t in both))}.</p>"
        elif both:
            pick = f"<h2>Which one fits you</h2><p>Korean reviewers praise both for the same things ({esc(', '.join(t.lower() for t in both))}), so price, size and availability are the better tiebreakers.</p>"
        others = [p for p, q in pairs.items() if q['cat'] == cat and p != path and q.get('last') == today]
        more = ''.join(f'<li><a href="{BASE}{p}">{esc(short_name(hist[pairs[p]["a"]]["r"]))} vs {esc(short_name(hist[pairs[p]["b"]]["r"]))}</a></li>'
                       for p in others if pairs[p]['a'] in hist and pairs[p]['b'] in hist)
        status = (f"Both are in Hwahae's top 3 {esc(noun)} today." if current else
                  f"This pair was last in Hwahae's top 3 {esc(noun)} on {esc(pr.get('last', ''))}; figures below are from then. See <a href=\"{BASE}c/{cat}/\">today's top 20</a>.")
        body = f"""<p class="kicker">Head to head · {esc(CAT[cat][0])} · updated {esc(up[:10])}</p><h1>{esc(na)} vs {esc(nb)}</h1>
<p class="lede">{status} Here is how they compare on Hwahae, Korea's biggest cosmetics review app, from Korean reviews rather than ads.</p>
{table}
<h2>The short version</h2><ul>{''.join(f'<li>{esc(p)}</li>' for p in pts)}</ul>
{pick}
<div class="grid"><div class="card"><h3><a href="{BASE}p/{pr['a']}/">{esc(na)}</a></h3>{buy_button(a)}</div>
<div class="card"><h3><a href="{BASE}p/{pr['b']}/">{esc(nb)}</a></h3>{buy_button(b)}</div></div>
{f'<h2>More {esc(noun)} comparisons</h2><ul>{more}</ul>' if more else ''}
<p><a href="{BASE}c/{cat}/">Full top 20 {esc(noun)}</a>{f' · <a href="{BASE}value/{cat}/">Best value {esc(noun)}</a>' if cat in VALUE_CATS else ''} · <a href="{BASE}compare/">All comparisons</a></p>
<p class="meta">We have not tested these products ourselves. This page compares Hwahae's public ratings, review counts, Korean list prices and the review topics Korean users mention most. {esc(LINK_NOTE)}</p>"""
        title = f"{na} vs {nb}: Korean Reviews Compared"
        desc = f"{na} vs {nb}: Hwahae rating, number of Korean reviews, Korean price per 100 ml and what reviewers praise, side by side."
        pin = f"compare-{cat}-{up[:7]}.jpg"  # the #1 vs #2 pin, when this is that pair and it has been rendered
        og = pin if (rank.get(pr['a']) == 1 and rank.get(pr['b']) == 2 and os.path.exists(f'{OUT}/pins/{pin}')) else default_img(path, up)
        NOINDEX.add(path)  # templated; reopen once a pair has a short written verdict (audit 2026-10-30)
        pages[path] = page(title, desc, path, body, up, f'<meta property="og:image" content="{BASE}pins/{og}"><meta name="twitter:card" content="summary_large_image">')
    # value pages: today's top 20 with rating 4.5+, sorted by Korean price per 100 ml
    vlinks = []
    for cat in VALUE_CATS:
        rk = by.get(cat)
        if not rk:
            continue
        items = sorted((r for r in rk['rows'] if r['rating'] >= 4.5 and per100(r)), key=per100)[:10]
        if len(items) < 5:
            continue
        noun = CAT[cat][1]
        lis = ''.join(f"""<li><div><div class="n">{i + 1}</div></div><div><div class="pn"><a href="{BASE}p/{r['id']}/" style="color:inherit;text-decoration:none">{esc(brand_label(r))} · {esc(name_label(r))}</a></div>
<div class="facts"><strong>₩{per100(r):,.0f} per 100 ml ({usd(per100(r))})</strong> · ₩{r['priceKrw']:,} for {esc(re.split(r'\s*/', str(r['size']))[0])} · ★ {r['rating']:.2f} · {r['reviews']:,} reviews · #{r['rank']} in the top 20</div>
<div class="tags">{''.join(f'<span>{esc(t)}</span>' for t in r['topics'])}</div><div class="links">{search_links(r)}</div></div></li>""" for i, r in enumerate(items))
        body = f"""<p class="kicker">Best value · updated {esc(up[:10])}</p><h1>Best value {esc(noun)}, by price per 100 ml</h1>
<p class="lede">Every product here is in Hwahae's top 20 {esc(noun)} today and rated 4.5 or higher by Korean reviewers. We sorted them by Korean list price per 100 ml, cheapest first, so big bottles and pricey minis compare fairly.</p>
<ol class="rank">{lis}</ol>
<p class="meta">Prices are Hwahae's Korean list prices; prices abroad are usually higher and change often, so check the size before you buy. Multi-packs are left out because their per-ml price is unclear. {esc(LINK_NOTE)}</p>
<p><a href="{BASE}c/{cat}/">Full top 20 {esc(noun)}</a> · <a href="{BASE}compare/">Head-to-head comparisons</a></p>"""
        ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': f'Best value {noun}, by price per 100 ml',
              'itemListOrder': 'https://schema.org/ItemListOrderAscending', 'numberOfItems': len(items),
              'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f"{BASE}p/{r['id']}/", 'name': short_name(r)} for i, r in enumerate(items)]}
        vpin = f"value-{cat}-{up[:7]}.jpg"
        head = (f'<meta property="og:image" content="{BASE}pins/{vpin if os.path.exists(f"{OUT}/pins/{vpin}") else default_img(f"value/{cat}/", up)}"><meta name="twitter:card" content="summary_large_image">'
                f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")}</script>')
        pages[f'value/{cat}/'] = page(f'Best Value {noun} by Price per 100 ml ({up[:10]})',
                                     f'The best-rated {noun} in Korea sorted by price per 100 ml. Hwahae top 20, rated 4.5+, Korean list prices with USD.',
                                     f'value/{cat}/', body, up, head)
        vlinks.append((cat, noun))
    # Seoul shopping list: #1 and #2 per category with Korean names to show in store
    order = [('cleansing', 'Cleanser'), ('toner', 'Toner'), ('serum', 'Serum'), ('cream', 'Moisturizer'), ('sunscreen', 'Sunscreen'),
             ('masks', 'Face mask'), ('cushion', 'Cushion'), ('lip', 'Lip')]
    secs, total = [], 0
    for cat, step in order:
        rk = by.get(cat)
        if not rk:
            continue
        lis = ''
        for r in rk['rows'][:2]:
            total += r['priceKrw'] if r is rk['rows'][0] and r.get('priceKrw') else 0
            lis += (f'<li><div class="pn"><a href="{BASE}p/{r["id"]}/">{esc(short_name(r))}</a></div>'
                    f'<div class="ko" style="font-size:18px">{esc(r["brand"])} {esc(r["name"])}</div>'
                    f'<div class="facts">#{r["rank"]} on Hwahae · ★ {r["rating"]:.2f} · {r["reviews"]:,} reviews'
                    + (f' · ₩{r["priceKrw"]:,} ({usd(r["priceKrw"])})' if r.get('priceKrw') else '')
                    + (f' · {esc(re.split(chr(92) + "s*/", str(r["size"]))[0])}' if r.get('size') else '') + '</div>'
                    # only hand-matched Amazon product pages here (no search links): readers browsing from home can still buy
                    + (f'<div class="links"><a href="{esc(amazon(short_name(r), r["id"]))}" rel="sponsored nofollow">Not in Seoul? See it on Amazon</a></div>'
                       if AMAZON_TAG and str(r['id']) in ASIN else '') + '</li>')
        secs.append(f'<h2>{esc(step)} <span class="meta">· <a href="{BASE}c/{cat}/">full top 20</a></span></h2><ol class="shop">{lis}</ol>')
    body = (f'<p class="kicker">Seoul shopping list · updated {esc(up[:10])}</p><h1>What to buy in Korea: a skincare shopping list from Korean reviews</h1>'
            '<p class="lede">The #1 and #2 product in each category on Hwahae, Korea\'s biggest cosmetics review app, with the Korean name to show '
            'shop staff and the Korean list price. Most top-ranked Hwahae products are sold at big Korean drugstore chains, but stock varies, so check in store.</p>'
            f'<p><strong>A full routine of every #1 (cleanser to sunscreen, plus mask, cushion and lip): about ₩{total:,} ({usd(total)}) at Korean list prices.</strong></p>'
            + ''.join(secs) +
            '<p class="meta">Tip: take a screenshot of this page; the Korean names (in grey) are what you show or search in the shop. Prices are Hwahae list prices and shops often run discounts. '
            'We have not tested these products; rankings are Hwahae\'s, from Korean reviews.</p>'
            f'<p><a href="{BASE}value/toner/">Best value by price per 100 ml</a> · <a href="{BASE}compare/">Head-to-head comparisons</a> · <a href="{BASE}guide/korean-skincare-routine/">Korean skincare routine</a></p>')
    pages['guide/seoul-shopping-list/'] = page(f'What to Buy in Korea: Skincare Shopping List with Korean Names and Prices ({up[:10]})',
                                               'Korea\'s #1 and #2 skincare in every category from Hwahae, with Korean names to show in store and Korean prices. Checked daily against Hwahae.',
                                               'guide/seoul-shopping-list/', body, up)
    groups = {}
    for p, q in pairs.items():
        if q['a'] in hist and q['b'] in hist and p in pages:
            groups.setdefault(q['cat'], []).append((q.get('last') != today, p, q))
    hub = ''
    for cat in COMPARE_CATS:
        if cat in groups:
            lis = ''.join(f'<li><a href="{BASE}{p}">{esc(short_name(hist[q["a"]]["r"]))} vs {esc(short_name(hist[q["b"]]["r"]))}</a>{" (older pair)" if old else ""}</li>'
                          for old, p, q in sorted(groups[cat]))
            hub += f'<div class="card"><h3>{esc(CAT[cat][0])}</h3><ul>{lis}</ul></div>'
    val = ''.join(f'<li><a href="{BASE}value/{c}/">Best value {esc(n)}</a></li>' for c, n in vlinks)
    pages['compare/'] = page('Korean Skincare Compared: Head-to-Head by Korean Reviews',
                             'Side-by-side comparisons of the top 3 products in each Hwahae category: ratings, reviews, price per 100 ml and what Korean reviewers praise.',
                             'compare/', f'<p class="kicker">Head to head</p><h1>Korean skincare, compared</h1><p class="lede">The top 3 of each Hwahae category, side by side: rating, number of Korean reviews, price per 100 ml and what reviewers praise. Checked every day.</p><div class="grid">{hub}</div>'
                             + (f'<h2>Best value by price per 100 ml</h2><ul>{val}</ul>' if val else ''), up)
    return pages


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
<p>How it is made: a script collects the public rankings every morning and builds these pages automatically. Translations are AI-assisted; we verify official English brand names against brand and retailer pages and leave a transliteration when we cannot confirm one.</p>
<h2>What we do not do</h2>
<p>We do not test products ourselves and we do not write fake reviews. Rankings are Hwahae's, not ours. K-Beauty Now is independent and not affiliated with Hwahae.</p>
<h2>Analytics</h2>
<p>We count page views with Cloudflare Web Analytics, which sets no cookies and does not track individual visitors.</p>
<h2>Links</h2>
<p>Store links help you find a product abroad. Some links may earn us a commission at no extra cost to you; this never changes the ranking order, which comes straight from Hwahae.</p>"""
    pages['privacy/'] = page('Privacy Policy: K-Beauty Now', 'What K-Beauty Now collects (almost nothing), analytics and affiliate links.', 'privacy/',
        '<p class="kicker">Privacy</p><h1>Privacy policy</h1>'
        '<p>K-Beauty Now has no accounts, forms or comments, so we do not collect your name, email or any personal details.</p>'
        '<h2>Analytics</h2><p>We count page views with Cloudflare Web Analytics. It does not use cookies or local storage and does not track you across sites; '
        'it records things like the page visited, referrer, country and device type in aggregate.</p>'
        '<h2>Affiliate links</h2><p>Some links go to stores such as Amazon. If you click one, that store may set its own cookies to credit us for a purchase, '
        'under its own privacy policy. We earn a commission on some purchases at no extra cost to you; it never changes the ranking order.</p>'
        '<h2>Hosting</h2><p>The site is hosted on GitHub Pages, which may log standard request data (such as IP address) for security.</p>'
        f'<h2>Changes</h2><p>We will update this page if anything changes. Last updated {esc(up[:10])}.</p>', up)
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
        pages['guide/korean-sunscreen/'] = page('Best Korean Sunscreen: SPF50+ PA++++ Picks from Hwahae', 'How to choose a Korean sunscreen (SPF50+, PA++++, mineral vs chemical) and the 5 sunscreens Korean Hwahae users rank highest today.', 'guide/korean-sunscreen/', g, up)

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
    pages['guide/korean-skincare-routine/'] = page('Korean Skincare Routine Order: 5 Steps and Korea\'s #1 Pick for Each',
        'The Korean skincare routine in the right order: cleanser, toner, serum, moisturizer, sunscreen, with the product Korean Hwahae users rank #1 for each step today.',
        'guide/korean-skincare-routine/', routine, up)
    movers = trending(data)
    if movers:
        items = ''.join(
            f'<li><div><div class="n">{r["rank"]}</div><div class="d">{delta(r)}</div></div><div>'
            f'<div class="pn"><a href="{BASE}p/{r["id"]}/" style="color:inherit;text-decoration:none">{esc(brand_label(r))} · {esc(name_label(r))}</a></div>'
            f'<div class="facts">#{r["rank"]} in {esc(where)} · ★ {r["rating"]:.2f} · {r["reviews"]:,} reviews</div>'
            f'<div class="tags">{"".join(f"<span>{esc(t)}</span>" for t in r["topics"])}</div>{card_buy(r)}</div></li>'
            for _, r, where, rk in movers)
        tr = (f'<p class="kicker">Trending · updated {esc(up[:10])}</p><h1>Trending Korean skincare right now: what is climbing in Korea</h1>'
              '<p class="lede">The products moving up fastest across all of Hwahae\'s rankings today, plus new entries. "▲5" means up five places since Hwahae\'s previous ranking. '
              'One day of movement can be noise, so treat this as a watch list, not a verdict.</p>'
              f'<ol class="rank">{items}</ol><p><a href="{BASE}c/all/">See the overall top 20</a> · <a href="{BASE}guide/">Buying guides</a></p>')
        pages['trending/'] = page('Trending Korean Skincare Right Now: Fastest Climbers on Hwahae',
            'The Korean skincare and makeup products climbing fastest on Hwahae, Korea\'s biggest cosmetics review app, today. English names, ratings and where to buy.',
            'trending/', tr, up)
    # Amazon picks: per routine step, the two best-ranked top-10 products sold on Amazon US (only when the Amazon tag is set)
    if AMAZON_TAG:
        steps_a = [('sunscreen', 'Sunscreen'), ('toner', 'Toner'), ('serum', 'Serum and essence'), ('cream', 'Moisturizer'),
                   ('cleansing', 'Cleanser'), ('masks', 'Sheet masks and pads'), ('cushion', 'Cushion foundation')]
        secs = []
        for cat, label in steps_a:
            rk = by.get(('category', cat))
            if not rk:
                continue
            cards = []
            # this page is for buying on Amazon: prefer the highest-ranked top-10 products we matched to an Amazon product page
            on_amz = [r for r in rk['rows'][:10] if str(r['id']) in ASIN]
            picks = (on_amz + [r for r in rk['rows'] if r not in on_amz])[:2]
            picks.sort(key=lambda r: r['rank'])
            for r in picks:
                q = f"{brand_label(r).split(' (')[0]} {name_label(r).split(' SPF')[0].split(' (')[0]}"
                tags = ', '.join(t.lower() for t in r['topics'][:3])
                cards.append(f'<div class="card"><p class="kicker">#{r["rank"]} {esc(label.lower())} in Korea</p>'
                             f'<h3><a href="{BASE}p/{r["id"]}/">{esc(brand_label(r))} {esc(name_label(r))}</a></h3>'
                             f'<p class="meta">★ {r["rating"]:.2f} from {r["reviews"]:,} Korean reviews' + (f'. Reviewers mention: {esc(tags)}.' if tags else '.') + '</p>'
                             f'<p><a class="buy" href="{esc(amazon(q, r["id"]))}" rel="sponsored nofollow">See it on Amazon</a></p></div>')
            secs.append(f'<h2>{esc(label)}</h2><div class="grid">{"".join(cards)}</div>')
        am = (f'<p class="kicker">Buying guide · updated {esc(up[:10])}</p><h1>Best Korean skincare on Amazon, picked by Korean reviewers</h1>'
              '<p class="lede">Amazon is full of Korean skincare, but its bestseller lists mix in sponsored and Western-made products. '
              'This list starts from the other side: the products Korean shoppers rate highest on Hwahae, Korea\'s biggest cosmetics review app, today, '
              'two per routine step: the highest-ranked ones we found on Amazon US, linked to the Amazon product page (or to an Amazon search when we could not match one).</p>'
              '<p class="meta">Check the seller before you buy: look for the brand\'s official store or "Ships from Amazon" to avoid fakes. Formulas sold abroad can differ slightly from the Korean version.</p>'
              + ''.join(secs) +
              f'<p class="meta">{esc(LINK_NOTE)}</p><p><a href="{BASE}guide/korean-skincare-routine/">Korean routine order</a> · <a href="{BASE}trending/">What is trending in Korea</a></p>')
        pages['guide/korean-skincare-on-amazon/'] = page('Best Korean Skincare on Amazon: Picks from Korean Reviewers',
            'The Korean skincare products Korean reviewers rank highest on Hwahae today, two per routine step, each with a link to find it on Amazon.',
            'guide/korean-skincare-on-amazon/', am, up)
    names = {'korean-sunscreen': 'Korean sunscreen', 'korean-skincare-routine': 'Korean skincare routine order', 'korean-skincare-on-amazon': 'Best Korean skincare on Amazon'} | {k: GUIDES[k][3].split(':')[0].replace('Best ', '') for k in GUIDES}
    hub = ('<p class="kicker">Guides</p><h1>Korean skincare buying guides</h1><p class="lede">Short, practical guides to each step of a Korean routine, each with the five products Korean Hwahae users rank highest today.</p>'
           '<p>How to use them: start with the step you are missing rather than replacing everything. Most Korean routines that hold up are short: '
           'a gentle cleanser, a hydrating toner, one serum for your main concern, a moisturizer and sunscreen every morning. '
           'The rankings tell you what Korean reviewers rate highly overall; they do not know your skin, so patch-test anything new and change one product at a time.</p><div class="grid">') + ''.join(
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
        pins.append({'title': t, 'sub': 'Most mentioned by Korean reviewers', 'date': up, 'file': f, 'items': [
            {'brand': brand_label(r).split(' (')[0], 'name': name_label(r).split(' SPF')[0].split(' (')[0], 'rating': r['rating'], 'reviews': r['reviews']}
            for r in rk['rows'][:5]]})
        top = ', '.join(f"{brand_label(r).split(' (')[0]} {name_label(r).split(' SPF')[0].split(' (')[0]}" for r in rk['rows'][:3])
        items.append(f"<item><title>{esc(t)} ({up})</title><link>{href}</link><guid isPermaLink=\"false\">{rk['type']}-{rk['slug']}-{up}</guid>"
                     f"<pubDate>{pub}</pubDate><description>{esc('Hwahae top 5 today: ' + top + '. Ranked by Korean reviewers.')}</description>"
                     f"<enclosure url=\"{BASE}pins/{f}\" type=\"image/jpeg\" length=\"0\"/></item>")
    mv = trending(data, 5)
    if len(mv) >= 3:
        f = f"trending-{up}.jpg"
        pins.append({'title': 'Trending in Korea: fastest-climbing K-beauty today', 'sub': 'Fastest climbers on Hwahae', 'date': up, 'file': f, 'items': [
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
        pins.append({'title': f'Best {b} products, ranked by Korean reviewers', 'sub': 'Best-ranked on Hwahae', 'date': up, 'file': f, 'items': [
            {'brand': b, 'name': name_label(h['r']).split(' SPF')[0].split(' (')[0], 'rating': h['r']['rating'], 'reviews': h['r']['reviews']} for h in hs[:5]]})
        top = ', '.join(name_label(h['r']).split(' SPF')[0].split(' (')[0] for h in hs[:3])
        items.append(f"<item><title>{esc('Best ' + b + ' products, ranked by Korean reviewers')}</title><link>{BASE}brand/{brand_slug(b)}/</link><guid isPermaLink=\"false\">brand-{brand_slug(b)}-{month}</guid>"
                     f"<pubDate>{pub}</pubDate><description>{esc(f'{len(hs)} {b} products have made a Hwahae top 20 in Korea. Top picks: {top}. Ratings and review counts from Korean reviewers.')}</description>"
                     f"<enclosure url=\"{BASE}pins/{f}\" type=\"image/jpeg\" length=\"0\"/></item>")
    # concern pins, monthly
    for topic in ('Non-sticky', 'Non-irritating', 'No breakouts', 'Fixes inner dryness', 'Soothing', 'Pore care'):
        slug, h1, lede = CONCERNS[topic]
        hs = sorted((h for h in hist.values() if topic in h['r']['topics']), key=lambda h: (h['r']['topics'].index(topic), -h['r']['rating']))
        if len(hs) < 4:
            continue
        f = f"concern-{slug}-{month}.jpg"
        t = h1.split(':')[0].replace(', according to Korean reviewers', '')
        pins.append({'title': t, 'sub': 'Most mentioned by Korean reviewers', 'date': up, 'file': f, 'items': [
            {'brand': brand_label(h['r']).split(' (')[0], 'name': name_label(h['r']).split(' SPF')[0].split(' (')[0], 'rating': h['r']['rating'], 'reviews': h['r']['reviews']} for h in hs[:5]]})
        items.append(f"<item><title>{esc(t)}</title><link>{BASE}concern/{slug}/</link><guid isPermaLink=\"false\">concern-{slug}-{month}</guid>"
                     f"<pubDate>{pub}</pubDate><description>{esc(lede + ' Ranked from Hwahae, Korea' + chr(39) + 's biggest cosmetics review app.')}</description>"
                     f"<enclosure url=\"{BASE}pins/{f}\" type=\"image/jpeg\" length=\"0\"/></item>")
    # value pins (price per 100 ml), monthly; they go to the guides board
    for cat in VALUE_CATS:
        rk = by.get(('category', cat))
        if not rk:
            continue
        vs = sorted((r for r in rk['rows'] if r['rating'] >= 4.5 and per100(r)), key=per100)[:5]
        if len(vs) < 5:
            continue
        noun = CAT[cat][1]
        t = f'Best value {noun}: what Koreans pay per 100 ml'
        f = f"value-{cat}-{month}.jpg"
        pins.append({'title': t, 'sub': 'Hwahae top 20, rated 4.5+', 'date': up, 'file': f, 'cta': 'All 10 best-value picks and where to buy →', 'items': [
            {'brand': brand_label(r).split(' (')[0], 'name': name_label(r).split(' SPF')[0].split(' (')[0], 'rating': r['rating'], 'reviews': r['reviews'],
             'meta': f"₩{per100(r):,.0f} per 100 ml ({usd(per100(r))}) · ★ {r['rating']:.2f}"} for r in vs]})
        top = ', '.join(short_name(r) for r in vs[:3])
        items.append(f"<item><title>{esc(t)}</title><link>{BASE}value/{cat}/</link><guid isPermaLink=\"false\">value-{cat}-{month}</guid>"
                     f"<pubDate>{pub}</pubDate><description>{esc(f'The best-rated {noun.lower()} in Korea, sorted by Korean price per 100 ml. Cheapest top-rated picks: {top}.')}</description>"
                     f"<enclosure url=\"{BASE}pins/{f}\" type=\"image/jpeg\" length=\"0\"/></item>")
    # compare pins: #1 vs #2 of each category, monthly, on the guides board
    for cat in COMPARE_CATS:
        rk = by.get(('category', cat))
        if not rk or len(rk['rows']) < 2:
            continue
        a, b = rk['rows'][0], rk['rows'][1]
        path = compare_path(a, b)
        side = lambda r: {'brand': brand_label(r).split(' (')[0], 'name': name_label(r).split(' SPF')[0].split(' (')[0], 'rank': r['rank'],
                          'rating': r['rating'], 'reviews': r['reviews'], 'price': (f"₩{r['priceKrw']:,} ({usd(r['priceKrw'])})" if r.get('priceKrw') else ''),
                          'per100': (f"₩{per100(r):,.0f} per 100 ml" if per100(r) and cat in VALUE_CATS else ''), 'tags': r['topics'][:3]}
        t = f"{short_name(a)} vs {short_name(b)}"
        f = f"compare-{cat}-{month}.jpg"
        pins.append({'title': t, 'date': up, 'file': f, 'vs': [side(a), side(b)], 'kicker': f"Korea's #1 vs #2 {CAT[cat][1].replace('Korean ', '').lower()}"})
        items.append(f"<item><title>{esc(t + ': Korean reviews compared')}</title><link>{BASE}{path}</link><guid isPermaLink=\"false\">compare-{cat}-{month}</guid>"
                     f"<pubDate>{pub}</pubDate><description>{esc(f'Korea' + chr(39) + f's #1 and #2 {CAT[cat][1].lower()} on Hwahae, side by side: rating, number of Korean reviews, Korean price and what reviewers praise.')}</description>"
                     f"<enclosure url=\"{BASE}pins/{f}\" type=\"image/jpeg\" length=\"0\"/></item>")
    all_items = list(items)
    # pick by the real KST date, not the ranking date: Hwahae can go days without updating, and evergreen
    # pins (guides, concerns, brands) should still go out daily; unchanged rankings are skipped by their sig
    kst_today = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date().isoformat()
    pins, items = select_pins(pins, items, kst_today)
    json.dump({'pins': pins}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pins.json'), 'w'), ensure_ascii=False)
    # two feeds so each Pinterest board stays on topic: rankings, trending and products -> rss.xml;
    # guides, concerns and brands -> rss-guides.xml (board "Korean Skincare Guides")
    evergreen = ('guide/', 'concern/', 'brand/', 'value/', 'compare/')
    is_ever = lambda it: re.search(r'<link>[^<]*/(%s)' % '|'.join(evergreen), it)
    is_skin = lambda it: '<guid isPermaLink="false">skin-' in it
    main_items = [it for it in items if not is_ever(it) and not is_skin(it)]

    # guides feed: every evergreen pin chosen in the last 30 days (a feed must never be empty; guids keep repeats out)
    try:
        st = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'pin_state.json')))
    except Exception:
        st = {}
    d0 = datetime.date.fromisoformat(up)
    recent = {u for u, v in st.items() if (d0 - datetime.date.fromisoformat(v['date'])).days <= 30}
    guide_items = [it for it in all_items if is_ever(it) and re.search(r'<link>([^<]+)</link>', it).group(1) in recent]
    if not guide_items:  # first run: seed with the routine guide so Pinterest accepts the feed
        guide_items = [it for it in all_items if '/guide/korean-skincare-routine/' in it][:1]

    # skin-type rankings get their own feed for the board 'Korean Skincare by Skin Type' (keeps every board alive)
    skin_items = [it for it in items if is_skin(it)] or [it for it in all_items if is_skin(it)][:1]

    def feed(title, desc, its):
        return (f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{title}</title><link>{BASE}</link>'
                f'<description>{desc}</description>{"".join(its)}</channel></rss>')
    open(f'{OUT}/rss-skin.xml', 'w').write(feed('K-Beauty Now by skin type', 'Korea\'s top-rated skincare for dry, oily, combination, sensitive and acne-prone skin, from Hwahae.', skin_items))
    open(f'{OUT}/rss-guides.xml', 'w').write(feed('K-Beauty Now guides', 'How to choose Korean skincare, by step, concern and brand, from Hwahae rankings.', guide_items))
    return feed('K-Beauty Now', 'Korea\'s top-rated K-beauty from Hwahae, in English, checked daily.', main_items)


PIN_CAP = 8  # per day; Pinterest treats repetitive automated pins as spam


def select_pins(pins, items, today):
    """Publish only pins that carry something new: a ranking whose top 5 changed, at most once a week per URL,
    weekly product pins at most once every 4 weeks per product, evergreen pins at most monthly and two a day.
    Same-day rebuilds are idempotent (today's picks are kept). State: data/pin_state.json."""
    import datetime as dt
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'pin_state.json')
    try:
        state = json.load(open(path))
    except Exception:
        state = {}
    d0 = dt.date.fromisoformat(today)
    cand = []
    for p, it in zip(pins, items):
        url = re.search(r'<link>([^<]+)</link>', it).group(1)
        guid = re.search(r'>([^<]+)</guid>', it).group(1)
        if 'items' in p and not guid.startswith(('brand-', 'concern-', 'value-')):
            kind, cool, prio = ('trending', 7, 0) if guid.startswith('trending-') else ('ranking', 7, 1)
            sig = '|'.join(x['name'] for x in p['items'])
        elif 'product' in p:
            kind, cool, prio, sig = 'product', 28, 2, guid
        else:
            kind, cool, prio, sig = 'evergreen', 30, 3, guid
        st = state.get(url)
        if st and st['date'] == today:
            cand.append((-1, p, it, url, sig))  # already picked today
            continue
        if st and (d0 - dt.date.fromisoformat(st['date'])).days < cool:
            continue
        if st and kind in ('ranking', 'trending') and st.get('sig') == sig:
            continue
        cand.append((prio, p, it, url, sig))
    cand.sort(key=lambda c: c[0])
    # keep one slot for an evergreen pin (guide, concern, brand) so the guides board gets something most days
    ever = next((c for c in cand if c[0] == 3), None)
    if ever and not any(c[0] == -1 for c in cand):
        cand.remove(ever)
        cand.insert(0, ever)
    picked, n_ever = [], 0
    for prio, p, it, url, sig in cand:
        if len(picked) >= PIN_CAP:
            break
        if prio == 3:
            if n_ever >= 2:
                continue
            n_ever += 1
        picked.append((p, it, url, sig))
    for p, it, url, sig in picked:
        state[url] = {'date': today, 'sig': sig}
    json.dump(state, open(path, 'w'), ensure_ascii=False, indent=0, sort_keys=True)
    return [p for p, *_ in picked], [it for _, it, *_ in picked]


def index_page(data):
    up = data['updatedAt']
    cards = []
    for rk in data['rankings']:
        name = CAT[rk['slug']][0] if rk['type'] == 'category' else f"Skincare for {SKIN[rk['slug']]}"
        href = f"{BASE}c/{rk['slug']}/" if rk['type'] == 'category' else f"{BASE}skin/{rk['slug']}/"
        top = ''.join(f'<li><a href="{BASE}p/{r["id"]}/" style="color:inherit">{esc(brand_label(r).split(" (")[0])} {esc(name_label(r).split(" SPF")[0])}</a></li>' for r in rk['rows'][:5])
        cards.append(f'<div class="card"><h3><a href="{href}">{esc(name)}</a></h3><ol>{top}</ol></div>')
    allrk = next((rk for rk in data['rankings'] if rk['type'] == 'category' and rk['slug'] == 'all'), None)
    TOP3 = ''
    if allrk:
        TOP3 = ('<h2>Korea\'s top 3 today</h2><ol class="rank">' + ''.join(row_html(r) for r in allrk['rows'][:3])
                + f'</ol><p><a href="{BASE}c/all/">See the full top 20</a></p>')
    # Reels/TikTok end on "Link in bio → tap '<label>'" (ops/shorts.mjs TAP): keep these labels in sync with it.
    jump = ''.join(f'<a href="{BASE}{p}"{" class=hot" if hot else ""}>{esc(l)}</a>' for l, p, hot in JUMP)
    body = f"""<p class="kicker">Checked daily against Hwahae</p><h1>What Korean reviewers rate highest in K-beauty</h1>
<p class="lede">Hwahae (화해) is the review app Koreans check before buying cosmetics. We put its top-20 rankings into English: names, ratings, prices and what reviewers praise.</p>
<p class="meta" style="margin-bottom:4px">Came from a video? Tap what you saw:</p><nav class="jump">{jump}</nav>
<p class="meta">Last ranking update: {esc(up)} KST</p>
{TOP3}
<h2>Start here</h2><div class="grid">
<div class="card"><h3><a href="{BASE}guide/korean-skincare-routine/">Korean skincare routine</a></h3><p class="meta">The 5 steps in order, with Korea's #1 pick for each.</p></div>
<div class="card"><h3><a href="{BASE}guide/korean-sunscreen/">Best Korean sunscreen</a></h3><p class="meta">SPF50+ PA++++, mineral or chemical, and today's top 5.</p></div>
<div class="card"><h3><a href="{BASE}guide/korean-skincare-on-amazon/">Korean skincare on Amazon</a></h3><p class="meta">Korea's top-rated picks per step, linked to Amazon.</p></div>
<div class="card"><h3><a href="{BASE}concern/">Shop by concern</a></h3><p class="meta">Non-sticky, soothing, no breakouts, pores, dehydrated skin.</p></div>
<div class="card"><h3><a href="{BASE}guide/seoul-shopping-list/">Seoul shopping list</a></h3><p class="meta">Korea's #1 and #2 per category, with Korean names to show in store.</p></div>
<div class="card"><h3><a href="{BASE}compare/">Head to head</a></h3><p class="meta">Korea's top 3 in each category, compared side by side.</p></div>
<div class="card"><h3><a href="{BASE}ingredient/">By ingredient</a></h3><p class="meta">Hyaluronic acid, ceramide, cica: Korea's top-rated picks.</p></div>
<div class="card"><h3><a href="{BASE}brand/">Best by brand</a></h3><p class="meta">Torriden, Round Lab, Anua and more, ranked by Korean reviewers.</p></div>
<div class="card"><h3><a href="{BASE}trending/">Trending in Korea</a></h3><p class="meta">What is climbing fastest on Hwahae today.</p></div>{WEEK_CARD[0]}
<div class="card"><h3><a href="{BASE}guide/">Guides by skin type</a></h3><p class="meta">Dry, oily, combination, sensitive and acne-prone skin.</p></div></div>
<h2>By category</h2><div class="grid">{''.join(c for c, rk in zip(cards, data['rankings']) if rk['type'] == 'category')}</div>
<h2>By skin type</h2><div class="grid">{''.join(c for c, rk in zip(cards, data['rankings']) if rk['type'] == 'skin')}</div>"""
    return page('K-Beauty Now: Korea\'s Top-Rated Skincare and Makeup, Ranked by Korean Reviewers',
                'Hwahae\'s Korean cosmetics rankings in English, checked daily: top 20 skincare, sunscreen, serum, toner, cushion and more, plus picks by skin type.',
                '', body, up)


def threads_posts(data):
    """Daily text posts for Threads (one per category, rotating), saved to data/threads.json."""
    import datetime
    # keyed by the real KST date: Hwahae can skip days, and a stale ranking date would make the poster
    # think today's post already went out (threads_log keys are date-slot)
    up = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date().isoformat()
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
                f"\nFull top 20 and where to buy: {BASE}c/{rk['slug']}/\n\nAuto-translated from Hwahae (AI-assisted, not sponsored).")
        text = re.sub(r'\b([A-Za-z])\.([A-Za-z]{2,})', r'\1. \2', text)  # 'S.NATURE' would be auto-linked as a domain
        if len(text) > 495:  # Threads limit is 500 characters
            text = re.sub(r'\. Most-mentioned: [^\n]*', '', text, count=1)
        if len(text) > 495:
            text = text.replace(' (the review app Koreans check before buying)', '')
        text = text[:500]
        posts.append({'category': rk['slug'], 'topic': 'K Beauty', 'text': text})
    # every other day the nightly slot (2) carries a value post instead: price per 100 ml across the top-rated shelf
    by = {rk['slug']: rk for rk in data['rankings'] if rk['type'] == 'category'}
    vc = [c for c in VALUE_CATS if c in by]
    if day % 3 == 2:  # every third night: #1 vs #2 head to head
        cc = [c for c in COMPARE_CATS if c in by and len(by[c]['rows']) >= 2]
        if cc and len(posts) > 2:
            c = cc[(day // 3) % len(cc)]
            a, b = by[c]['rows'][0], by[c]['rows'][1]
            noun = CAT[c][1].replace('Korean ', '')
            def line(r):
                v = per100(r)
                return (f"{short_name(r)}: {r['rating']:.2f} from {r['reviews']:,} reviews" + (f", ₩{v:,.0f} per 100 ml" if v and c in VALUE_CATS else '')
                        + (f". Reviewers mention: {', '.join(t.lower() for t in r['topics'][:2])}" if r['topics'] else ''))
            text = (f"#1 vs #2 {noun} in Korea right now (Hwahae, the review app Koreans check before buying):\n\n"
                    f"#1 {line(a)}\n\n#2 {line(b)}\n\nWhich fits you, side by side: {BASE}{compare_path(a, b)}\n\n"
                    "Translated from Hwahae with AI help. Not sponsored.")
            text = re.sub(r'\b([A-Za-z])\.([A-Za-z]{2,})', r'\1. \2', text)
            if len(text) > 495:
                text = re.sub(r'\. Reviewers mention: [^\n]*', '', text)
            posts[2] = {'category': 'compare-' + c, 'topic': 'K Beauty', 'text': text[:500]}
    elif day % 3 == 1 and vc:
        c = vc[(day // 2) % len(vc)]
        vs = sorted((r for r in by[c]['rows'] if r['rating'] >= 4.5 and per100(r)), key=per100)
        if len(vs) >= 4:
            noun = CAT[c][1]
            lo, hi = per100(vs[0]), per100(vs[-1])
            text = (f"Best value {noun}, by what Koreans pay per 100 ml (Hwahae top 20, all rated 4.5+):\n\n"
                    + ''.join(f"{i}. {short_name(r)}: ₩{per100(r):,.0f} ({usd(per100(r))})\n" for i, r in enumerate(vs[:3], 1))
                    + f"\nSame top-rated shelf, up to {hi / lo:.0f}x price gap per ml. Full list: {BASE}value/{c}/\n\n"
                    "Korean list prices from Hwahae, translated with AI help. Not sponsored.")
            text = re.sub(r'\b([A-Za-z])\.([A-Za-z]{2,})', r'\1. \2', text)[:500]
            if len(posts) > 2:
                posts[2] = {'category': 'value-' + c, 'topic': 'K Beauty', 'text': text}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'threads.json')
    json.dump({'date': up, 'posts': posts}, open(path, 'w'), ensure_ascii=False, indent=1)


def main():
    import hashlib
    data = json.load(open(os.path.join(os.path.dirname(__file__), 'data', 'latest.json')))
    os.makedirs(OUT, exist_ok=True)
    day = data['updatedAt'][:10]
    hpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'page_hash.json')
    try:
        hashes = json.load(open(hpath))
    except Exception:
        hashes = {}
    lastmod = {}

    def write(path, h):
        os.makedirs(f'{OUT}/{path}', exist_ok=True)
        open(f'{OUT}/{path}index.html', 'w').write(h)
        main_part = h.split('<main>', 1)[-1]
        key = hashlib.sha1(re.sub(r'\d{4}-\d{2}-\d{2}( \d{2}:\d{2}:\d{2})?', '', main_part).encode()).hexdigest()[:16]
        old = hashes.get(path)
        if not old or old[0] != key:
            hashes[path] = [key, day]
        lastmod[path] = hashes[path][1]

    urls = ['']
    for rk in data['rankings']:
        path, h = ranking_page(rk, data['updatedAt'])
        write(path, h)
        urls.append(path)
    for path, h in list(product_pages(data).items()) + list(extra_pages(data).items()):
        write(path, h)
        if path not in NOINDEX:
            urls.append(path)
    for path, h in compare_pages(data).items():  # needs data/products.json from product_pages
        write(path, h)
        if path not in NOINDEX:
            urls.append(path)
    home = index_page(data)
    open(f'{OUT}/index.html', 'w').write(home)
    lastmod[''] = day
    open(f'{OUT}/rss.xml', 'w').write(pins_and_rss(data))
    threads_posts(data)
    # English names for ops/shorts.mjs (vertical video slideshows)
    json.dump({'labels': {sl: CAT[sl][1].replace('Korean ', '') for sl in CAT},
               'products': {str(r['id']): {'brand': brand_label(r).split(' (')[0], 'name': name_label(r).split(' (')[0]}
                            for rk in data['rankings'] for r in rk['rows']}},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'shorts_names.json'), 'w'), ensure_ascii=False)
    json.dump(hashes, open(hpath, 'w'), indent=0, sort_keys=True)
    open(f'{OUT}/sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                          + ''.join(f'<url><loc>{BASE}{u}</loc><lastmod>{lastmod.get(u, day)}</lastmod></url>' for u in urls) + '</urlset>')
    open(f'{OUT}/robots.txt', 'w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
    open(f'{OUT}/.nojekyll', 'w').write('')
    missing = sorted({r['name'] for rk in data['rankings'] for r in rk['rows'] if r['name'] not in N})
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'untranslated.txt'), 'w').write('\n'.join(missing))
    print(len(urls), 'pages;', len(missing), 'untranslated')

if __name__ == '__main__':
    main()
