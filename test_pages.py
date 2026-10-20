import urllib.request
import urllib.error
import time

time.sleep(1)

# urllib follows redirects by default; for redirect-expected pages we check
# that they DO redirect (not 200 directly) using a no-redirect opener
no_redirect = urllib.request.build_opener(urllib.request.HTTPErrorProcessor)

pages = [
    # (name, url, expected_status, follow_redirects)
    ('Homepage/Catalogue',      'http://127.0.0.1:8000/',                             200, True),
    ('Login page',              'http://127.0.0.1:8000/accounts/login/',               200, True),
    ('Register page',           'http://127.0.0.1:8000/accounts/register/',            200, True),
    ('Create Listing',          'http://127.0.0.1:8000/listings/new/',                 200, True),
    ('Search results',          'http://127.0.0.1:8000/listings/search/?q=yam',        200, True),
    ('Price Broadcasts Feed',   'http://127.0.0.1:8000/broadcasts/',                   200, True),
    ('Post Broadcast form',     'http://127.0.0.1:8000/broadcasts/create/',            200, True),
    ('Seasonal Guide',          'http://127.0.0.1:8000/seasonal/guide/',               200, True),
    ('Harvest Calendar',        'http://127.0.0.1:8000/seasonal/calendar/',            200, True),
    ('Farm Stories Feed',       'http://127.0.0.1:8000/stories/',                      200, True),
    ('Unread Count API',        'http://127.0.0.1:8000/notifications/unread-count/',   200, True),
    ('Django Admin (redirect)', 'http://127.0.0.1:8000/django-admin/',                 302, False),
    ('Orders (redirect)',       'http://127.0.0.1:8000/orders/',                       302, False),
    ('Dashboard (redirect)',    'http://127.0.0.1:8000/accounts/dashboard/',           302, False),
    ('Notifications (redir)',   'http://127.0.0.1:8000/notifications/',                302, False),
    ('404 handler',             'http://127.0.0.1:8000/no-such-page/',                 404, True),
]

ok = 0
fail = 0
for name, url, expected, follow in pages:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TestBot/1.0'})
        if follow:
            with urllib.request.urlopen(req, timeout=8) as r:
                got = r.status
        else:
            with no_redirect.open(req, timeout=8) as r:
                got = r.status
        if got == expected:
            print(f'  PASS [{got}]  {name}')
            ok += 1
        else:
            print(f'  FAIL [got {got}, want {expected}]  {name}')
            fail += 1
    except urllib.error.HTTPError as e:
        got = e.code
        if got == expected:
            print(f'  PASS [{got}]  {name}')
            ok += 1
        else:
            print(f'  FAIL [got {got}, want {expected}]  {name}')
            fail += 1
    except Exception as ex:
        print(f'  FAIL [ERR]  {name} — {ex}')
        fail += 1

print()
print(f'Results: {ok} PASSED  {fail} FAILED  ({len(pages)} total)')
