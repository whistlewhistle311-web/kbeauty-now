"""Runs in GitHub Actions with the APIFY_TOKEN secret (never printed).
1) Applies ops/apify_actors.json (title/description edits, build requests) to our actors.
2) Saves public stats of every koreadata-lab actor to data/apify_stats.json for the dashboard."""
import json, os, urllib.request, datetime

TOKEN = os.environ.get('APIFY_TOKEN', '')
API = 'https://api.apify.com/v2'


def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


here = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(here, 'apify_actors.json')))
log = []
if TOKEN:
    for a in cfg.get('actors', []):
        patch = {k: a[k] for k in ('title', 'description', 'seoTitle', 'seoDescription') if k in a}
        if patch:
            try:
                call('PUT', f"/acts/{a['id']}", patch); log.append(f"{a['id']} updated {sorted(patch)}")
            except Exception as e:
                log.append(f"{a['id']} update failed: {e}")
        if a.get('build'):
            try:
                b = call('POST', f"/acts/{a['id']}/builds?version={a.get('version', '0.0')}&tag=latest")
                log.append(f"{a['id']} build {b['data']['id']}")
            except Exception as e:
                log.append(f"{a['id']} build failed: {e}")
stats = []
with urllib.request.urlopen(f'{API}/store?username=koreadata-lab&limit=50', timeout=60) as r:
    for a in json.load(r)['data']['items']:
        s = a.get('stats', {})
        stats.append({'name': a['name'], 'title': a['title'], 'users30': s.get('totalUsers30Days'), 'users': s.get('totalUsers'),
                      'runs': s.get('totalRuns'), 'pricing': (a.get('currentPricingInfo') or {}).get('pricingModel')})
if TOKEN:
    try:
        me = call('GET', '/users/me')['data']
        stats_extra = {'plan': me.get('plan', {}).get('id')}
    except Exception as e:
        stats_extra = {'error': str(e)[:80]}
else:
    stats_extra = {'note': 'no token'}
out = {'at': datetime.datetime.utcnow().isoformat(timespec='minutes') + 'Z', 'actors': stats, 'account': stats_extra, 'log': log}
json.dump(out, open(os.path.join(here, '..', 'data', 'apify_stats.json'), 'w'), ensure_ascii=False, indent=1)
print('\n'.join(log) or 'no changes', '|', len(stats), 'actors')
