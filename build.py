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
.links{font-size:13.5px;margin-top:6px}.links a{color:var(--accent);margin-right:12px}
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


def search_links(r):
    q = f"{brand_label(r).split(' (')[0]} {name_label(r).split(' SPF')[0].split(' (')[0]}"
    oy = 'https://global.oliveyoung.com/display/search?query=' + urllib.parse.quote(q)
    ys = 'https://www.yesstyle.com/en/list.html?q=' + urllib.parse.quote(q)
    return f'<a href="{oy}" rel="nofollow">Olive Young Global</a><a href="{ys}" rel="nofollow">YesStyle</a><a href="{esc(r["url"])}" rel="nofollow">Hwahae page (KR)</a>'


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


def page(title, desc, path, body, updated):
    url = BASE + path
    nav = ''.join(f'<a href="{BASE}c/{s}/">{v[0]}</a>' for s, v in CAT.items() if s in ('skincare', 'sunscreen', 'serum', 'toner', 'cushion'))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="google-site-verification" content="0oISjJafxIxC-LdVeihPqTQ3o9DoxV5FSNgvVZB-tps">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">
<style>{CSS}</style></head><body>
<header class="top"><div><a class="home" href="{BASE}">K-Beauty Now</a>{nav}<a href="{BASE}guide/korean-sunscreen/">Sunscreen guide</a><a href="{BASE}about/">About</a></div></header>
<main>{body}
<footer>Rankings come from the public ranking pages of Hwahae (화해), Korea's largest cosmetics review app, and are refreshed daily. Ranking updated {esc(updated)} KST.
Product names are translated by K-Beauty Now; brand names marked with Korean in brackets are transliterations, not official English names. Prices are Hwahae list prices in Korea; USD is approximate at {KRW_PER_USD:,} KRW per USD.
Need this data as JSON for your shop or trend report? The same rankings are available as an API on <a href="https://apify.com/koreadata-lab/hwahae-kbeauty-ranking-tracker">Apify (Hwahae K-Beauty Ranking Tracker)</a>.
Store links are search links. K-Beauty Now is independent and not affiliated with Hwahae, Olive Young or YesStyle.</footer></main></body></html>"""


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
    return path, page(title, desc, path, body, updated)


def product_pages(data):
    prods = {}
    for rk in data['rankings']:
        label = CAT[rk['slug']][0] if rk['type'] == 'category' else f"Skincare for {SKIN[rk['slug']]}"
        href = f"{BASE}c/{rk['slug']}/" if rk['type'] == 'category' else f"{BASE}skin/{rk['slug']}/"
        for r in rk['rows']:
            p = prods.setdefault(r['id'], {'r': r, 'ranks': []})
            p['ranks'].append((label, href, r['rank']))
    pages = {}
    for pid, p in prods.items():
        r = p['r']
        nm = f"{brand_label(r).split(' (')[0]} {name_label(r)}"
        ranks = ''.join(f'<li>#{rk} in <a href="{h}">{esc(l)}</a></li>' for l, h, rk in sorted(p['ranks'], key=lambda x: x[2]))
        tags = ''.join(f'<span>{esc(t)}</span>' for t in r['topics'])
        price = f"₩{r['priceKrw']:,} ({usd(r['priceKrw'])})" if r['priceKrw'] else 'not listed'
        body = f"""<p class="kicker">Hwahae ranking profile</p><h1>{esc(nm)}</h1>
<p class="ko">{esc(r['brand'])} {esc(r['name'])}</p>
<div class="card"><div class="facts">★ <strong>{r['rating']:.2f}</strong> on Hwahae from {r['reviews']:,} Korean reviews</div>
<div class="facts">Korean list price: {price}{(' · ' + esc(r['size'])) if r['size'] else ''}</div>
<div class="tags">{tags}</div><div class="links">{search_links(r)}</div></div>
<h2>Where it ranks in Korea today</h2><ul>{ranks}</ul>
<p class="meta">Tags are the review topics Korean Hwahae users mention most for this product. Ratings and ranks change daily.</p>"""
        title = f"{nm}: Hwahae Rating {r['rating']:.2f} and Korea Ranking"
        desc = f"{nm} is rated {r['rating']:.2f} from {r['reviews']:,} Korean reviews on Hwahae. See where it ranks in Korea today, its Korean price and what reviewers praise."
        pages[f"p/{pid}/"] = page(title, desc, f"p/{pid}/", body, data['updatedAt'])
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
    return pages


def pins_and_rss(data):
    up = data['updatedAt'][:10]
    pins, items = [], []
    for rk in data['rankings']:
        if rk['type'] == 'category':
            t = f"Top {CAT[rk['slug']][1].replace('Korean ', 'Korean ')} in Korea"
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
                     f"<description>{esc('Hwahae top 5 today: ' + top + '. Ranked by Korean reviewers.')}</description>"
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
        top = ''.join(f'<li>{esc(brand_label(r).split(" (")[0])} {esc(name_label(r).split(" SPF")[0])}</li>' for r in rk['rows'][:5])
        cards.append(f'<div class="card"><h3><a href="{href}">{esc(name)}</a></h3><ol>{top}</ol></div>')
    body = f"""<p class="kicker">Updated daily from Hwahae</p><h1>What Koreans are actually buying in K-beauty</h1>
<p class="lede">Hwahae (화해) is the review app Koreans check before buying cosmetics. This site turns its public top-20 rankings into English every day: product names, ratings, review counts, prices and what reviewers praise, by category and by skin type.</p>
<p class="meta">Last ranking update: {esc(up)} KST</p>
<h2>By category</h2><div class="grid">{''.join(c for c, rk in zip(cards, data['rankings']) if rk['type'] == 'category')}</div>
<h2>By skin type</h2><div class="grid">{''.join(c for c, rk in zip(cards, data['rankings']) if rk['type'] == 'skin')}</div>"""
    return page('K-Beauty Now: Korea\'s Top-Rated Skincare and Makeup, Updated Daily',
                'Hwahae\'s Korean cosmetics rankings in English, updated daily: top 20 skincare, sunscreen, serum, toner, cushion and more, plus picks by skin type.',
                '', body, up)


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
