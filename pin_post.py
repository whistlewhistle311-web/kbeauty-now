"""Post today's ranking pins to our own Pinterest business account via API v5.

Runs in GitHub Actions after pins.mjs. Needs the PINTEREST_TOKEN secret (an access token for our own
account with boards:read, boards:write, pins:read, pins:write). Without the secret it does nothing.
Posted pins are remembered in data/posted.json so a re-run never posts twice.
"""
import json, os, re, sys, time, urllib.request, urllib.error

TOKEN = os.environ.get('PINTEREST_TOKEN', '').strip()
API = 'https://api.pinterest.com/v5'
BASE = 'https://whistlewhistle311-web.github.io/kbeauty-now/'
BOARDS = {'category': 'Korea Top-Rated K-Beauty', 'skin': 'Korean Skincare by Skin Type'}
ROOT = os.path.dirname(os.path.abspath(__file__))
MAX_PER_RUN = 15


def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        print('HTTP', e.code, path, e.read()[:300].decode(errors='replace'))
        raise


def board_ids():
    have = {}
    bookmark = None
    while True:
        res = call('GET', '/boards?page_size=100' + (f'&bookmark={bookmark}' if bookmark else ''))
        for b in res.get('items', []):
            have[b['name']] = b['id']
        bookmark = res.get('bookmark')
        if not bookmark:
            break
    for name in BOARDS.values():
        if name not in have:
            have[name] = call('POST', '/boards', {'name': name, 'privacy': 'PUBLIC',
                                                  'description': 'Korea\'s top-rated K-beauty from Hwahae, translated into English daily by K-Beauty Now.'})['id']
    return have


def main():
    if not TOKEN:
        print('PINTEREST_TOKEN not set; skipping')
        return
    pins = json.load(open(os.path.join(ROOT, 'pins.json')))['pins']
    rss = open(os.path.join(ROOT, 'docs', 'rss.xml')).read()
    items = re.findall(r'<item><title>(.*?)</title><link>(.*?)</link>.*?<description>(.*?)</description>', rss)
    posted_path = os.path.join(ROOT, 'data', 'posted.json')
    posted = json.load(open(posted_path)) if os.path.exists(posted_path) else {}
    ids = board_ids()
    n = 0
    for p, (title, link, desc) in zip(pins, items):
        if p['file'] in posted or n >= MAX_PER_RUN:
            continue
        kind = 'skin' if p['file'].startswith('skin-') else 'category'
        body = {'board_id': ids[BOARDS[kind]], 'title': p['title'][:100], 'link': link,
                'description': desc.replace('&amp;', '&')[:500], 'alt_text': f"{p['title']}: Hwahae top 5 list"[:500],
                'media_source': {'source_type': 'image_url', 'url': BASE + 'pins/' + p['file']}}
        res = call('POST', '/pins', body)
        posted[p['file']] = res.get('id')
        n += 1
        time.sleep(20)  # spread requests; well under Pinterest rate limits
    json.dump(posted, open(posted_path, 'w'), indent=0)
    print('posted', n)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # never fail the whole daily build because of Pinterest
        print('pin_post failed:', e)
        sys.exit(0)
