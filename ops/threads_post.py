"""Posts one of today's K-Beauty posts (data/threads.json) to Threads via the official API.
Runs in GitHub Actions with THREADS_TOKEN (never printed).

Slot: the argument if given, otherwise the daily evening slot (2). The slot no longer depends on the UTC hour:
GitHub can start a scheduled run hours late (11/1 the 11:43 UTC run started at 17:14 and was skipped as 'hour 17').
The workflow runs several times a day; a post already in data/threads_log.json is never posted twice.
Every skip or failure that means a post did not go out is written to threads_log.json with a reason."""
import json, os, sys, urllib.request, urllib.parse, urllib.error, datetime, time
T = os.environ.get('THREADS_TOKEN', '')
here = os.path.dirname(os.path.abspath(__file__)); data = os.path.join(here, '..', 'data')
logp = os.path.join(data, 'threads_log.json')
log = json.load(open(logp)) if os.path.exists(logp) else []
now = datetime.datetime.now(datetime.timezone.utc)
stamp = now.isoformat(timespec='minutes')
kst_today = (now + datetime.timedelta(hours=9)).date()
DEFAULT_SLOT = 2


def save():
    json.dump(log[-200:], open(logp, 'w'), ensure_ascii=False, indent=1)


def note(key, reason):
    """Record why a post did not go out (once per key and reason, so reruns do not pile up lines)."""
    if not any(x.get('key') == key and x.get('reason') == reason for x in log):
        log.append({'key': key, 'reason': reason, 'at': stamp})
        save()
    print('skip:', reason)


if len(sys.argv) > 1 and sys.argv[1] == 'check':
    with urllib.request.urlopen('https://graph.threads.net/v1.0/me?fields=username&access_token=' + T, timeout=60) as r:
        print('token ok for', json.load(r).get('username')); sys.exit(0)

try:
    posts = json.load(open(os.path.join(data, 'threads.json')))
except Exception as e:
    note(f'{kst_today}-{DEFAULT_SLOT}-skip', f'threads.json unreadable: {type(e).__name__}'); sys.exit(0)

slot = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] != '' else DEFAULT_SLOT
key = f"{posts.get('date')}-{slot}"

if any(x.get('key') == key and x.get('id') for x in log):
    print('already posted', key); sys.exit(0)
if not T:
    note(key + '-skip', 'THREADS_TOKEN missing'); sys.exit(0)
if slot < 0 or slot >= len(posts.get('posts', [])):
    note(key + '-skip', f'slot {slot} not in threads.json ({len(posts.get("posts", []))} posts)'); sys.exit(0)
try:
    age = (kst_today - datetime.date.fromisoformat(posts['date'])).days
except Exception:
    age = 99
if age > 1:
    # the daily build did not refresh threads.json: do not post days-old rankings as if they were today's
    note(f'{kst_today}-{slot}-skip', f"threads.json is from {posts.get('date')} ({age} days old); daily build did not run"); sys.exit(0)

p = posts['posts'][slot]


def call(path, **q):
    q['access_token'] = T
    req = urllib.request.Request('https://graph.threads.net/v1.0/' + path, data=urllib.parse.urlencode(q).encode(), method='POST')
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


try:
    c = call('me/threads', media_type='TEXT', text=p['text'], topic_tag=p.get('topic', 'K Beauty'))
    time.sleep(5)
    r = call('me/threads_publish', creation_id=c['id'])
    log.append({'key': key, 'id': r.get('id'), 'category': p['category'], 'at': stamp})
    print('posted', key, r.get('id'))
except urllib.error.HTTPError as e:
    body = e.read().decode()[:300]
    log.append({'key': key + '-error', 'error': f'{e.code} {body}', 'at': stamp})
    print('error', e.code, body)
except Exception as e:  # network errors, bad JSON, missing fields: still leave a trace instead of a silent gap
    log.append({'key': key + '-error', 'error': f'{type(e).__name__}: {str(e)[:200]}', 'at': stamp})
    print('error', type(e).__name__, e)
save()
