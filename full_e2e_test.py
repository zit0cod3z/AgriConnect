"""
AgroConnect — Full End-to-End Functional Test
Tests every major user action: register, login, post listing,
make offer, notifications, broadcasts, stories, admin panel, logout.
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agroconnect.settings')
sys.path.insert(0, r'c:\Users\KIZITO\AgriConnect\agroconnect')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.listings.models import Listing
from apps.negotiations.models import Offer, Deal
from apps.orders.models import Order
from apps.notifications.models import Notification
from apps.broadcasts.models import PriceBroadcast
from apps.stories.models import FarmStory

Customer = get_user_model()

passed = []
failed = []

def check(label, fn):
    try:
        result = fn()
        passed.append(label)
        print(f"  ✅  {label}")
        return result
    except Exception as e:
        failed.append((label, str(e)))
        print(f"  ❌  {label}")
        print(f"       {e}")
        return None

# ── Clean up test data ────────────────────────────────────────────
Customer.objects.filter(email__in=['buyer@test.ng','farmer@test.ng']).delete()
Listing.objects.filter(contact_phone='08011110000').delete()

# ── Clients ───────────────────────────────────────────────────────
buyer_client  = Client(enforce_csrf_checks=False)
farmer_client = Client(enforce_csrf_checks=False)
anon_client   = Client(enforce_csrf_checks=False)

print("\n" + "="*60)
print("1. REGISTRATION")
print("="*60)

def test_register_buyer():
    r = buyer_client.post('/accounts/register/', {
        'full_name': 'Test Buyer',
        'email': 'buyer@test.ng',
        'phone': '08011110001',
        'state': 'Lagos',
        'password': 'BuyerPass@123',
        'confirm_password': 'BuyerPass@123',
    })
    assert r.status_code in (200, 302), f"Got {r.status_code}"
    assert Customer.objects.filter(email='buyer@test.ng').exists(), "User not created"

def test_register_farmer():
    r = farmer_client.post('/accounts/register/', {
        'full_name': 'Test Farmer',
        'email': 'farmer@test.ng',
        'phone': '08011110002',
        'state': 'Kano',
        'password': 'FarmerPass@123',
        'confirm_password': 'FarmerPass@123',
    })
    assert r.status_code in (200, 302), f"Got {r.status_code}"
    assert Customer.objects.filter(email='farmer@test.ng').exists(), "Farmer not created"

check("Register buyer account", test_register_buyer)
check("Register farmer account", test_register_farmer)

print("\n" + "="*60)
print("2. LOGIN")
print("="*60)

def test_login_buyer():
    buyer_client.logout()
    r = buyer_client.post('/accounts/login/', {
        'email': 'buyer@test.ng',
        'password': 'BuyerPass@123',
    })
    assert r.status_code in (200, 302), f"Got {r.status_code}"
    # Check session has user
    from django.contrib.auth import SESSION_KEY
    assert SESSION_KEY in buyer_client.session, "User not in session after login"

def test_login_farmer():
    farmer_client.logout()
    r = farmer_client.post('/accounts/login/', {
        'email': 'farmer@test.ng',
        'password': 'FarmerPass@123',
    })
    assert r.status_code in (200, 302), f"Got {r.status_code}"
    from django.contrib.auth import SESSION_KEY
    assert SESSION_KEY in farmer_client.session, "Farmer not in session after login"

def test_login_wrong_password():
    c = Client(enforce_csrf_checks=False)
    r = c.post('/accounts/login/', {
        'email': 'buyer@test.ng',
        'password': 'WRONGPASSWORD',
    })
    from django.contrib.auth import SESSION_KEY
    assert SESSION_KEY not in c.session, "Should NOT be logged in with wrong password"

def test_login_admin():
    c = Client(enforce_csrf_checks=False)
    r = c.post('/django-admin/login/', {
        'username': 'admin@agro.com',
        'password': 'admin123',
        'next': '/django-admin/',
    })
    assert r.status_code in (200, 302), f"Got {r.status_code}"

check("Buyer login with correct password", test_login_buyer)
check("Farmer login with correct password", test_login_farmer)
check("Login with wrong password denied", test_login_wrong_password)
check("Django admin login", test_login_admin)

print("\n" + "="*60)
print("3. DASHBOARD")
print("="*60)

def test_dashboard():
    r = buyer_client.get('/accounts/dashboard/')
    assert r.status_code == 200, f"Dashboard returned {r.status_code}"
check("Authenticated dashboard returns 200", test_dashboard)

def test_dashboard_redirect_anon():
    r = anon_client.get('/accounts/dashboard/')
    assert r.status_code == 302, f"Expected 302, got {r.status_code}"
    assert 'login' in r['Location'], "Should redirect to login"

check("Unauthenticated dashboard redirects to login", test_dashboard_redirect_anon)

print("\n" + "="*60)
print("4. CATALOGUE & SEARCH")
print("="*60)

def test_catalogue():
    r = anon_client.get('/')
    assert r.status_code == 200
    assert b'Marketplace' in r.content or b'listings' in r.content.lower()
check("Catalogue page loads", test_catalogue)

def test_search_empty():
    r = anon_client.get('/listings/search/')
    assert r.status_code == 200
check("Search page loads (no query)", test_search_empty)

def test_search_with_query():
    r = anon_client.get('/listings/search/?q=tomato')
    assert r.status_code == 200
check("Search with query returns 200", test_search_with_query)

print("\n" + "="*60)
print("5. POST A LISTING (farmer)")
print("="*60)

listing_ref = None

def test_post_listing():
    global listing_ref
    r = farmer_client.post('/listings/new/', {
        'produce_name': 'Fresh Tomatoes E2E',
        'category': 'vegetables',
        'quantity': '200',
        'unit': 'kg',
        'price_per_unit': '800',
        'farm_state': 'Kano',
        'farm_lga': 'Kano Municipal',
        'contact_phone': '08011110000',
        'description': 'Very fresh tomatoes from Kano',
        'group_buy_eligible': '',
    })
    assert r.status_code in (200, 302), f"Got {r.status_code}"
    listing = Listing.objects.filter(contact_phone='08011110000').first()
    assert listing is not None, "Listing was not saved to DB"
    listing_ref = listing.reference_code
    assert len(listing_ref) == 19, f"Bad ref code: {listing_ref}"

check("Farmer can post a listing", test_post_listing)

def test_listing_detail():
    if not listing_ref:
        raise AssertionError("No listing ref — depends on post listing test")
    r = anon_client.get(f'/listings/{listing_ref}/')
    assert r.status_code == 200, f"Got {r.status_code}"
    assert b'Tomatoes' in r.content
check("Listing detail page loads", test_listing_detail)

def test_listing_search_finds_it():
    r = anon_client.get('/listings/search/?q=Tomatoes+E2E')
    assert r.status_code == 200
    assert b'Tomatoes E2E' in r.content
check("Search finds posted listing", test_listing_search_finds_it)

def test_anon_cannot_post_rate_limited():
    # Anon can post (guest listing) — just test it works
    r = anon_client.post('/listings/new/', {
        'produce_name': 'Anon Yam',
        'category': 'tubers',
        'quantity': '50',
        'unit': 'bags',
        'price_per_unit': '12000',
        'farm_state': 'Benue',
        'farm_lga': 'Gboko',
        'contact_phone': '08099990000',
        'description': 'Test anon listing',
    })
    assert r.status_code in (200, 302), f"Got {r.status_code}"
    Listing.objects.filter(contact_phone='08099990000').delete()
check("Anonymous user can post a guest listing", test_anon_cannot_post_rate_limited)

print("\n" + "="*60)
print("6. MAKE AN OFFER")
print("="*60)

offer_id = None

def test_submit_offer():
    global offer_id
    if not listing_ref:
        raise AssertionError("Depends on post listing")
    r = buyer_client.post(f'/negotiations/offer/{listing_ref}/', {
        'proposed_price': '700',
        'proposed_quantity': '50',
        'message': 'Can you do 700 per kg?',
    })
    assert r.status_code in (200, 302), f"Got {r.status_code}"
    offer = Offer.objects.filter(
        listing__reference_code=listing_ref
    ).first()
    assert offer is not None, "Offer not saved"
    offer_id = offer.pk
check("Buyer can submit an offer", test_submit_offer)

def test_negotiation_thread():
    if not listing_ref:
        raise AssertionError("Depends on post listing")
    r = buyer_client.get(f'/negotiations/thread/{listing_ref}/')
    assert r.status_code == 200, f"Got {r.status_code}"
check("Negotiation thread page loads", test_negotiation_thread)

def test_accept_offer():
    if not offer_id:
        raise AssertionError("Depends on submit offer")
    r = farmer_client.post(f'/negotiations/accept/{offer_id}/')
    assert r.status_code in (200, 302), f"Got {r.status_code}"
    from apps.negotiations.models import Deal
    deal = Deal.objects.filter(offer_id=offer_id).first()
    assert deal is not None, "Deal not created on accept"
    assert Order.objects.filter(deal=deal).exists(), "Order not created from deal"
check("Farmer can accept offer → Deal + Order created", test_accept_offer)

print("\n" + "="*60)
print("7. ORDERS")
print("="*60)

def test_order_list():
    r = buyer_client.get('/orders/')
    assert r.status_code == 200
check("Order list page loads for buyer", test_order_list)

def test_order_detail():
    order = Order.objects.filter(customer__email='buyer@test.ng').first()
    if not order:
        raise AssertionError("No order found — depends on accept offer")
    r = buyer_client.get(f'/orders/{order.pk}/')
    assert r.status_code == 200
check("Order detail page loads", test_order_detail)

def test_confirm_order_pod():
    order = Order.objects.filter(customer__email='buyer@test.ng').first()
    if not order:
        raise AssertionError("No order")
    r = buyer_client.post(f'/orders/{order.pk}/confirm/', {
        'payment_method': 'pod',
    })
    assert r.status_code in (200, 302), f"Got {r.status_code}"
    order.refresh_from_db()
    assert order.status == 'confirmed', f"Expected confirmed, got {order.status}"
check("Buyer can confirm order with POD", test_confirm_order_pod)

print("\n" + "="*60)
print("8. NOTIFICATIONS")
print("="*60)

def test_notifications_list():
    r = buyer_client.get('/notifications/')
    assert r.status_code == 200
check("Notifications list page loads", test_notifications_list)

def test_unread_count_api():
    r = buyer_client.get('/notifications/unread-count/')
    assert r.status_code == 200
    import json
    data = json.loads(r.content)
    assert 'count' in data
check("Unread count API returns JSON", test_unread_count_api)

def test_mark_notification_read():
    notif = Notification.objects.filter(customer__email='buyer@test.ng').first()
    if not notif:
        raise AssertionError("No notifications found")
    r = buyer_client.post(f'/notifications/mark-read/{notif.pk}/')
    assert r.status_code == 200
    import json
    data = json.loads(r.content)
    assert 'count' in data
check("Mark notification as read", test_mark_notification_read)

print("\n" + "="*60)
print("9. PRICE BROADCASTS")
print("="*60)

def test_broadcast_feed():
    r = anon_client.get('/broadcasts/')
    assert r.status_code == 200
check("Broadcast feed loads", test_broadcast_feed)

def test_create_broadcast():
    from django.utils import timezone
    r = anon_client.post('/broadcasts/create/', {
        'broadcaster_name': 'Test Buyer',
        'broadcaster_phone': '08055550000',
        'produce_name': 'Onions',
        'offered_price': '500',
        'quantity_wanted': '100',
        'unit': 'kg',
        'state': 'Lagos',
        'message': 'Need fresh onions',
    })
    assert r.status_code in (200, 302), f"Got {r.status_code}"
    assert PriceBroadcast.objects.filter(broadcaster_phone='08055550000').exists()
    PriceBroadcast.objects.filter(broadcaster_phone='08055550000').delete()
check("Anonymous user can create a broadcast", test_create_broadcast)

print("\n" + "="*60)
print("10. SEASONAL GUIDE & CALENDAR")
print("="*60)

def test_seasonal_guide():
    r = anon_client.get('/seasonal/guide/')
    assert r.status_code == 200
check("Seasonal guide loads", test_seasonal_guide)

def test_harvest_calendar():
    r = anon_client.get('/seasonal/calendar/')
    assert r.status_code == 200
check("Harvest calendar loads", test_harvest_calendar)

def test_calendar_zone_filter():
    r = anon_client.get('/seasonal/calendar/?zone=south_west')
    assert r.status_code == 200
check("Harvest calendar zone filter works", test_calendar_zone_filter)

print("\n" + "="*60)
print("11. FARM STORIES")
print("="*60)

def test_stories_feed():
    r = anon_client.get('/stories/')
    assert r.status_code == 200
check("Stories feed loads", test_stories_feed)

def test_create_story():
    r = buyer_client.post('/stories/create/', {
        'title': 'My First Harvest',
        'body': 'This year I grew the most amazing tomatoes in my farm near Kano.',
        'listing': '',
    })
    assert r.status_code in (200, 302), f"Got {r.status_code}"
    assert FarmStory.objects.filter(title='My First Harvest').exists(), "Story not saved"
check("Authenticated user can create a story", test_create_story)

def test_story_like():
    story = FarmStory.objects.filter(is_approved=True).last()
    if not story:
        raise AssertionError("No approved story found")
    r = buyer_client.post(f'/stories/{story.pk}/like/')
    assert r.status_code in (200, 302), f"Got {r.status_code}"
    story.refresh_from_db()
    assert story.like_count >= 1, "Like count not incremented"
check("User can like a story", test_story_like)

print("\n" + "="*60)
print("12. ADMIN PANEL")
print("="*60)

def test_admin_panel_requires_staff():
    r = buyer_client.get('/admin-panel/')
    assert r.status_code in (302, 403), f"Expected 302/403, got {r.status_code}"
check("Admin panel blocks non-staff users", test_admin_panel_requires_staff)

def test_admin_panel_staff_access():
    admin_client = Client(enforce_csrf_checks=False)
    admin_client.login(username='admin@agro.com', password='admin123')
    r = admin_client.get('/admin-panel/')
    assert r.status_code == 200, f"Got {r.status_code}"
check("Admin panel accessible by staff", test_admin_panel_staff_access)

def test_admin_audit_log():
    admin_client = Client(enforce_csrf_checks=False)
    admin_client.login(username='admin@agro.com', password='admin123')
    r = admin_client.get('/admin-panel/audit-log/')
    assert r.status_code == 200
check("Admin audit log page loads", test_admin_audit_log)

def test_admin_moderation():
    admin_client = Client(enforce_csrf_checks=False)
    admin_client.login(username='admin@agro.com', password='admin123')
    r = admin_client.get('/admin-panel/moderation/')
    assert r.status_code == 200
check("Admin moderation queue loads", test_admin_moderation)

print("\n" + "="*60)
print("13. LOGOUT")
print("="*60)

def test_logout():
    r = buyer_client.post('/accounts/logout/')
    assert r.status_code in (200, 302), f"Got {r.status_code}"
    from django.contrib.auth import SESSION_KEY
    assert SESSION_KEY not in buyer_client.session, "Session not cleared after logout"
check("Logout clears session", test_logout)

def test_after_logout_dashboard_redirects():
    r = buyer_client.get('/accounts/dashboard/')
    assert r.status_code == 302
    assert 'login' in r['Location']
check("After logout, dashboard redirects to login", test_after_logout_dashboard_redirects)

# ── Clean up ────────────────────────────────────────────────────────
from apps.negotiations.models import CounterOffer, Deal
from apps.listings.models import FreshnessScore
from apps.stories.models import FarmStoryLike
customers_qs = Customer.objects.filter(email__in=['buyer@test.ng','farmer@test.ng'])
FreshnessScore.objects.filter(customer__in=customers_qs).delete()
FarmStoryLike.objects.filter(customer__in=customers_qs).delete()
Notification.objects.filter(customer__in=customers_qs).delete()
Order.objects.filter(customer__in=customers_qs).delete()
CounterOffer.objects.filter(offer__customer__in=customers_qs).delete()
Deal.objects.filter(offer__customer__in=customers_qs).delete()
Offer.objects.filter(customer__in=customers_qs).delete()
Listing.objects.filter(contact_phone__in=['08011110000','08099990000']).delete()
FarmStory.objects.filter(farmer_name__in=['Test Buyer','Test Farmer']).delete()
PriceBroadcast.objects.filter(broadcaster_phone='08055550000').delete()
customers_qs.delete()

# ── Summary ─────────────────────────────────────────────────────────
print("\n" + "="*60)
print(f"  TOTAL   : {len(passed)+len(failed)}")
print(f"  PASSED  : {len(passed)}  ✅")
print(f"  FAILED  : {len(failed)}  {'✅' if not failed else '❌'}")
print("="*60)
if failed:
    print("\nFAILURES:")
    for label, err in failed:
        print(f"  ❌ {label}")
        print(f"     → {err}")
else:
    print("  All end-to-end tests passed! 🌿")
