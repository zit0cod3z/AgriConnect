"""
Test registration and login logic directly against the DB.
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agroconnect.settings')
sys.path.insert(0, r'c:\Users\KIZITO\AgriConnect\agroconnect')
django.setup()

from django.contrib.auth import authenticate, get_user_model
from apps.accounts.services import create_customer, is_account_locked

Customer = get_user_model()

passed = []
failed = []

def check(label, fn):
    try:
        result = fn()
        passed.append(label)
        print(f'  ✅  {label}')
        return result
    except Exception as e:
        failed.append((label, str(e)))
        print(f'  ❌  {label} — {e}')
        return None

# ── Clean up test user if exists ──
Customer.objects.filter(email='test@agroconnect.ng').delete()

# ── Test 1: Register new user ──
customer = check('Register new user', lambda: create_customer(
    full_name='Test Farmer',
    email='test@agroconnect.ng',
    phone='08012345678',
    state='Lagos',
    password='TestPass123!'
))

# ── Test 2: Duplicate email rejected ──
def test_duplicate():
    try:
        create_customer('Test', 'test@agroconnect.ng', '08000', 'Kano', 'pass')
        raise AssertionError('Should have raised ValidationError')
    except Exception as e:
        if 'already exists' in str(e):
            return True
        raise
check('Duplicate email rejected', test_duplicate)

# ── Test 3: Authenticate with correct password ──
check('Authenticate correct password',
    lambda: authenticate(None, username='test@agroconnect.ng', password='TestPass123!') is not None
             or (_ for _ in ()).throw(AssertionError('authenticate() returned None')))

# ── Test 4: Authenticate with wrong password returns None ──
def test_wrong_pass():
    result = authenticate(None, username='test@agroconnect.ng', password='wrongpassword')
    assert result is None, f'Expected None, got {result}'
check('Wrong password returns None', test_wrong_pass)

# ── Test 5: Case-insensitive email lookup ──
def test_case_insensitive():
    u = Customer.objects.get(email__iexact='TEST@AGROCONNECT.NG')
    assert u.email == 'test@agroconnect.ng'
check('Case-insensitive email lookup', test_case_insensitive)

# ── Test 6: Admin superuser exists ──
def test_admin():
    u = Customer.objects.get(email='admin@agro.com')
    assert u.is_staff
    assert u.is_superuser
check('Admin superuser exists and is_staff=True', test_admin)

# ── Test 7: Authenticate admin ──
check('Admin can authenticate',
    lambda: authenticate(None, username='admin@agro.com', password='admin123') is not None
             or (_ for _ in ()).throw(AssertionError('Admin authenticate() returned None')))

# ── Test 8: Account not locked by default ──
def test_not_locked():
    u = Customer.objects.get(email='test@agroconnect.ng')
    assert not is_account_locked(u)
check('New account is not locked', test_not_locked)

# ── Clean up ──
Customer.objects.filter(email='test@agroconnect.ng').delete()

print()
print('=' * 50)
print(f'  PASSED : {len(passed)}')
print(f'  FAILED : {len(failed)}')
print('=' * 50)
if failed:
    for label, err in failed:
        print(f'  ❌ {label}: {err}')
else:
    print('  All auth tests passed! ✅')
