"""Runs in GitHub Actions with AWIN_TOKEN (never printed). Saves joined/pending programmes and last-30-day transactions."""
import json, os, urllib.request, datetime
T = os.environ.get('AWIN_TOKEN', ''); PID = '3138543'
now = datetime.datetime.now(datetime.timezone.utc)
out = {'at': now.isoformat(timespec='minutes'), 'joined': [], 'pending': [], 'transactions': [], 'totals': {}}
def get(path):
    req = urllib.request.Request('https://api.awin.com' + path, headers={'Authorization': f'Bearer {T}'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)
if T:
    try:
        for rel, key in (('joined', 'joined'), ('pending', 'pending')):
            for p in get(f'/publishers/{PID}/programmes?relationship={rel}'):
                out[key].append({'id': p.get('id'), 'name': p.get('name')})
        s = (now - datetime.timedelta(days=30)).strftime('%Y-%m-%dT00:00:00'); e = now.strftime('%Y-%m-%dT23:59:59')
        tx = get(f'/publishers/{PID}/transactions/?startDate={s}&endDate={e}&timezone=UTC')
        for t in tx:
            out['transactions'].append({'date': t.get('transactionDate'), 'advertiser': t.get('advertiserId'), 'status': t.get('commissionStatus'),
                                        'sale': (t.get('saleAmount') or {}).get('amount'), 'commission': (t.get('commissionAmount') or {}).get('amount'),
                                        'currency': (t.get('commissionAmount') or {}).get('currency')})
        out['totals'] = {'count': len(out['transactions']), 'commission': round(sum(x['commission'] or 0 for x in out['transactions']), 2)}
    except Exception as ex:
        out['error'] = str(ex)[:120]
else:
    out['note'] = 'no token'
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'awin_stats.json'), 'w'), ensure_ascii=False, indent=1)
print(len(out['joined']), 'joined', len(out['pending']), 'pending', out['totals'], out.get('error', ''))
