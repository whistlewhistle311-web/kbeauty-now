"""Runs in GitHub Actions with GUMROAD_TOKEN (never printed). Saves product sales totals to data/gumroad_stats.json."""
import json, os, urllib.request, urllib.parse, datetime
T = os.environ.get('GUMROAD_TOKEN', '')
out = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='minutes'), 'products': [], 'sales': []}
if T:
    def get(path, **q):
        q['access_token'] = T
        with urllib.request.urlopen('https://api.gumroad.com/v2/' + path + '?' + urllib.parse.urlencode(q), timeout=60) as r:
            return json.load(r)
    try:
        for p in get('products').get('products', []):
            out['products'].append({'name': p['name'], 'price_cents': p.get('price'), 'sales_count': p.get('sales_count'),
                                    'sales_usd_cents': p.get('sales_usd_cents'), 'published': p.get('published'), 'url': p.get('short_url')})
        for s in get('sales').get('sales', [])[:50]:
            out['sales'].append({'at': s.get('created_at'), 'product': s.get('product_name'), 'usd_cents': s.get('price'), 'country': s.get('country')})
    except Exception as e:
        out['error'] = str(e)[:120]
else:
    out['note'] = 'no token'
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'gumroad_stats.json'), 'w'), ensure_ascii=False, indent=1)
print(len(out['products']), 'products', len(out['sales']), 'sales', out.get('error', ''))
