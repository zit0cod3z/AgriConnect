"""
AgroConnect - Full URL smoke test.
Checks every public URL for 500 errors.
Auth-protected pages are expected to 302 → login (not 500).
"""
import urllib.request
import urllib.error
import time

BASE = 'http://127.0.0.1:8000'

URLS = [
    # ── Listings / Catalogue ──
    ('GET', '/',                                          [200]),
    ('GET', '/listings/new/',                             [200]),
    ('GET', '/listings/search/',                          [200]),
    ('GET', '/listings/search/?q=tomato',                 [200]),
    ('GET', '/listings/search/?q=yam&category=tubers',   [200]),

    # ── Accounts ──
    ('GET', '/accounts/register/',                        [200]),
    ('GET', '/accounts/login/',                           [200]),
    ('GET', '/accounts/dashboard/',                       [200, 302]),
    ('GET', '/accounts/password-reset/',                  [200]),
    ('GET', '/accounts/verify/badtoken/',                 [200, 302]),

    # ── Seasonal ──
    ('GET', '/seasonal/guide/',                           [200]),
    ('GET', '/seasonal/calendar/',                        [200]),
    ('GET', '/seasonal/calendar/?zone=north_west',        [200]),
    ('GET', '/seasonal/calendar/?zone=south_west',        [200]),

    # ── Broadcasts ──
    ('GET', '/broadcasts/',                               [200]),
    ('GET', '/broadcasts/create/',                        [200]),

    # ── Stories ──
    ('GET', '/stories/',                                  [200]),
    ('GET', '/stories/create/',                           [200, 302]),

    # ── Negotiations ──
    ('GET', '/negotiations/thread/XXXX-XXXX-XXXX-XXXX/', [200, 302, 404]),

    # ── Orders (login required) ──
    ('GET', '/orders/',                                   [200, 302]),
    ('GET', '/orders/99999/',                             [200, 302, 404]),

    # ── Payments (login required) ──
    ('GET', '/payments/initiate/99999/',                  [200, 302, 404]),
    ('GET', '/payments/callback/',                        [200, 302]),

    # ── Notifications ──
    ('GET', '/notifications/',                            [200, 302]),
    ('GET', '/notifications/unread-count/',               [200]),

    # ── Group Buy ──
    ('GET', '/groupbuy/join/99999/',                      [200, 302, 404, 405]),
    ('GET', '/groupbuy/leave/99999/',                     [200, 302, 404, 405]),

    # ── Admin panel (staff required) ──
    ('GET', '/admin-panel/',                              [200, 302, 403]),
    ('GET', '/admin-panel/audit-log/',                    [200, 302, 403]),
    ('GET', '/admin-panel/moderation/',                   [200, 302, 403]),

    # ── Django admin ──
    ('GET', '/django-admin/',                             [200, 302]),
    ('GET', '/django-admin/login/',                       [200]),

    # ── Error pages ──
    ('GET', '/this-page-does-not-exist/',                 [404]),
    ('GET', '/listings/no-such-ref-code/',                [200, 404]),
]

ok = fail = skip = 0
failures = []

for method, path, acceptable in URLS:
    url = BASE + path
    req = urllib.request.Request(url, headers={'User-Agent': 'SmokeTest/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception as ex:
        print(f'  ERR  {path}  →  {ex}')
        failures.append((path, f'exception: {ex}'))
        fail += 1
        continue

    if code == 500:
        print(f'  500 ❌  {path}')
        failures.append((path, '500 Internal Server Error'))
        fail += 1
    elif code in acceptable:
        print(f'  {code} ✓   {path}')
        ok += 1
    else:
        print(f'  {code} ?   {path}  (expected {acceptable})')
        skip += 1

print()
print('=' * 55)
print(f'  PASSED  : {ok}')
print(f'  UNEXPECTED: {skip}')
print(f'  500/ERR   : {fail}')
print('=' * 55)
if failures:
    print('FAILURES:')
    for p, reason in failures:
        print(f'  {p}  →  {reason}')
else:
    print('  No 500 errors found! ✅')
