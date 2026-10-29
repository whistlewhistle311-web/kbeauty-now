"""Posts one of today's 3 K-Beauty posts (data/threads.json) to Threads via the official API.
Runs in GitHub Actions with THREADS_TOKEN (never printed). Slot = which of the 3 posts, chosen by UTC hour.
Skips if that post was already published (data/threads_log.json)."""
import json, os, sys, urllib.request, urllib.parse, datetime
T = os.environ.get('THREADS_TOKEN', '')
here = os.path.dirname(os.path.abspath(__file__)); data = os.path.join(here, '..', 'data')
posts = json.load(open(os.path.join(data, 'threads.json')))
logp = os.path.join(data, 'threads_log.json')
log = json.load(open(logp)) if os.path.exists(logp) else []
hour = datetime.datetime.now(datetime.timezone.utc).hour
slot = int(sys.argv[1]) if len(sys.argv) > 1 else {23: 0, 0: 0, 4: 1, 5: 1, 11: 2, 12: 2}.get(hour, -1)
if not T or slot < 0 or slot >= len(posts['posts']):
    print('skip: token' if not T else f'skip: hour {hour}'); sys.exit(0)
key = f"{posts['date']}-{slot}"
if any(x.get('key') == key for x in log):
    print('already posted', key); sys.exit(0)
p = posts['posts'][slot]

def call(path, **q):
    q['access_token'] = T
    req = urllib.request.Request('https://graph.threads.net/v1.0/' + path, data=urllib.parse.urlencode(q).encode(), method='POST')
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)
try:
    c = call('me/threads', media_type='TEXT', text=p['text'], topic_tag=p.get('topic', 'K Beauty'))
    import time; time.sleep(5)
    r = call('me/threads_publish', creation_id=c['id'])
    log.append({'key': key, 'id': r.get('id'), 'category': p['category'], 'at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='minutes')})
    print('posted', key, r.get('id'))
except urllib.error.HTTPError as e:
    body = e.read().decode()[:300]
    log.append({'key': key + '-error', 'error': f'{e.code} {body}', 'at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='minutes')})
    print('error', e.code, body)
json.dump(log[-200:], open(logp, 'w'), ensure_ascii=False, indent=1)
