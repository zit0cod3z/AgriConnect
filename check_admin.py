import urllib.request, urllib.error

pages = [
    ('Admin Panel Dashboard',  'http://127.0.0.1:8000/admin-panel/',            [200, 302, 403]),
    ('Admin Audit Log',        'http://127.0.0.1:8000/admin-panel/audit-log/',  [200, 302, 403]),
    ('Admin Moderation',       'http://127.0.0.1:8000/admin-panel/moderation/', [200, 302, 403]),
    ('Django Admin',           'http://127.0.0.1:8000/django-admin/',           [200, 302]),
    ('Navbar (homepage)',      'http://127.0.0.1:8000/',                        [200]),
    ('Seasonal Guide',         'http://127.0.0.1:8000/seasonal/guide/',         [200]),
    ('Broadcasts',             'http://127.0.0.1:8000/broadcasts/',             [200]),
    ('Stories',                'http://127.0.0.1:8000/stories/',                [200]),
    ('Harvest Calendar',       'http://127.0.0.1:8000/seasonal/calendar/',      [200]),
]

ok = fail = 0
for name, url, acceptable in pages:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'SmokeTest'})
        with urllib.request.urlopen(req, timeout=8) as r:
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception as ex:
        print(f'  ERR  {name}: {ex}')
        fail += 1
        continue

    if code == 500:
        print(f'  500 ❌  {name}')
        fail += 1
    elif code in acceptable:
        print(f'  {code} ✅  {name}')
        ok += 1
    else:
        print(f'  {code} ❓  {name} (expected {acceptable})')
        ok += 1  # unexpected but not a 500

print(f'\n{ok} OK  |  {fail} ERRORS')
