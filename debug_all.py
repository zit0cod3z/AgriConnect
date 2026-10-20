"""
Reproduce all three reported bugs:
1. Django admin login fails
2. User registration fails
3. Listing create 500
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agroconnect.settings')
sys.path.insert(0, r'c:\Users\KIZITO\AgriConnect\agroconnect')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import authenticate, get_user_model
from apps.accounts.services import create_customer
from apps.listings.services import create_listing

Customer = get_user_model()

print("=" * 60)
print("BUG 1: Django Admin Login")
print("=" * 60)
u = Customer.objects.filter(email='admin@agro.com').first()
if u:
    print(f"  username field = '{u.username}'")
    print(f"  email field    = '{u.email}'")
    print(f"  is_staff       = {u.is_staff}")
    print(f"  is_active      = {u.is_active}")
    # Django admin authenticates via username field
    result = authenticate(None, username=u.username, password='admin123')
    print(f"  authenticate(username='{u.username}') => {result}")
    result2 = authenticate(None, username='admin@agro.com', password='admin123')
    print(f"  authenticate(username='admin@agro.com') => {result2}")
else:
    print("  No admin@agro.com found in DB!")

print()
print("=" * 60)
print("BUG 2: Registration")
print("=" * 60)
Customer.objects.filter(email='newuser@test.ng').delete()
try:
    c = create_customer('New User', 'newuser@test.ng', '08099999999', 'Lagos', 'Pass@1234')
    print(f"  create_customer => OK, pk={c.pk}, username='{c.username}'")
    auth = authenticate(None, username=c.username, password='Pass@1234')
    print(f"  authenticate after register => {auth}")
except Exception as e:
    print(f"  create_customer FAILED => {e}")
Customer.objects.filter(email='newuser@test.ng').delete()

print()
print("=" * 60)
print("BUG 3: Listing Create 500")
print("=" * 60)
try:
    listing = create_listing({
        'produce_name': 'Test Tomatoes',
        'category': 'vegetables',
        'quantity': '100',
        'unit': 'kg',
        'price_per_unit': '500.00',
        'farm_state': 'Lagos',
        'farm_lga': 'Ikeja',
        'contact_phone': '08011111111',
        'description': 'Fresh tomatoes',
    })
    print(f"  create_listing => OK, ref={listing.reference_code}")
    listing.delete()
except Exception as e:
    import traceback
    print(f"  create_listing FAILED => {e}")
    traceback.print_exc()

print()
print("=" * 60)
print("BUG 3b: ListingForm validation")
print("=" * 60)
try:
    from apps.listings.forms import ListingForm
    data = {
        'produce_name': 'Test Rice',
        'category': 'grains',
        'quantity': '200',
        'unit': 'bags',
        'price_per_unit': '25000',
        'farm_state': 'Kano',
        'farm_lga': 'Kano Municipal',
        'contact_phone': '08022222222',
        'description': 'Premium quality',
        'group_buy_eligible': False,
    }
    form = ListingForm(data)
    print(f"  form.is_valid() => {form.is_valid()}")
    if not form.is_valid():
        print(f"  form.errors => {form.errors}")
    else:
        print(f"  cleaned_data keys => {list(form.cleaned_data.keys())}")
except Exception as e:
    import traceback
    print(f"  ListingForm FAILED => {e}")
    traceback.print_exc()

print()
print("=" * 60)
print("BUG 3c: CreateListingView POST via test client")
print("=" * 60)
try:
    c2 = Client(enforce_csrf_checks=False)
    resp = c2.post('/listings/new/', {
        'produce_name': 'Test Yam',
        'category': 'tubers',
        'quantity': '50',
        'unit': 'bags',
        'price_per_unit': '15000',
        'farm_state': 'Benue',
        'farm_lga': 'Gboko',
        'contact_phone': '08033333333',
        'description': 'Fresh yam',
    })
    print(f"  POST /listings/new/ => HTTP {resp.status_code}")
    if resp.status_code == 500:
        # Get the exception from the response
        print("  500 ERROR — checking context...")
        if hasattr(resp, 'context') and resp.context:
            print(f"  context keys: {list(resp.context.keys()) if resp.context else 'None'}")
    elif resp.status_code in (200, 302):
        print(f"  OK — redirected to: {resp.get('Location', 'N/A')}")
except Exception as e:
    import traceback
    print(f"  Test client POST FAILED => {e}")
    traceback.print_exc()
