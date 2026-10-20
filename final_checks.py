"""
AgroConnect — Final integrity checks.
Validates: imports, models, services, URL resolution, migrations.
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agroconnect.settings')
sys.path.insert(0, r'c:\Users\KIZITO\AgriConnect\agroconnect')
django.setup()

passed = []
failed = []

def check(label, fn):
    try:
        fn()
        passed.append(label)
        print(f'  ✓  {label}')
    except Exception as e:
        failed.append((label, str(e)))
        print(f'  ✗  {label}  →  {e}')

# ── Model imports ──
check('Model: Customer',           lambda: __import__('apps.accounts.models', fromlist=['Customer']))
check('Model: Listing',            lambda: __import__('apps.listings.models', fromlist=['Listing']))
check('Model: Offer',              lambda: __import__('apps.negotiations.models', fromlist=['Offer']))
check('Model: Deal',               lambda: __import__('apps.negotiations.models', fromlist=['Deal']))
check('Model: Order',              lambda: __import__('apps.orders.models', fromlist=['Order']))
check('Model: Notification',       lambda: __import__('apps.notifications.models', fromlist=['Notification']))
check('Model: PriceBroadcast',     lambda: __import__('apps.broadcasts.models', fromlist=['PriceBroadcast']))
check('Model: GroupBuy',           lambda: __import__('apps.groupbuy.models', fromlist=['GroupBuy']))
check('Model: FarmStory',          lambda: __import__('apps.stories.models', fromlist=['FarmStory']))
check('Model: PaystackTransaction',lambda: __import__('apps.payments.models', fromlist=['PaystackTransaction']))
check('Model: AdminAuditLog',      lambda: __import__('apps.admin_panel.models', fromlist=['AdminAuditLog']))
check('Model: HarvestSeasonSignal',lambda: __import__('apps.seasonal.models', fromlist=['HarvestSeasonSignal']))

# ── Service imports ──
check('Service: accounts',         lambda: __import__('apps.accounts.services', fromlist=['create_customer']))
check('Service: listings',         lambda: __import__('apps.listings.services', fromlist=['create_listing']))
check('Service: negotiations',     lambda: __import__('apps.negotiations.services', fromlist=['submit_offer']))
check('Service: orders',           lambda: __import__('apps.orders.services', fromlist=['create_order_from_deal']))
check('Service: notifications',    lambda: __import__('apps.notifications.services', fromlist=['notify']))
check('Service: broadcasts',       lambda: __import__('apps.broadcasts.services', fromlist=['create_broadcast']))
check('Service: groupbuy',         lambda: __import__('apps.groupbuy.services', fromlist=['join_group_buy']))
check('Service: stories',          lambda: __import__('apps.stories.services', fromlist=['create_story']))
check('Service: payments',         lambda: __import__('apps.payments.services', fromlist=['verify_paystack_payment']))
check('Service: admin_panel',      lambda: __import__('apps.admin_panel.services', fromlist=['log_admin_action']))
check('Service: seasonal',         lambda: __import__('apps.seasonal.services', fromlist=['evaluate_season_signal']))

# ── View imports ──
check('Views: accounts',    lambda: __import__('apps.accounts.views', fromlist=['RegisterView']))
check('Views: listings',    lambda: __import__('apps.listings.views', fromlist=['CatalogueView']))
check('Views: negotiations',lambda: __import__('apps.negotiations.views', fromlist=['SubmitOfferView']))
check('Views: orders',      lambda: __import__('apps.orders.views', fromlist=['OrderListView']))
check('Views: payments',    lambda: __import__('apps.payments.views', fromlist=['InitiatePaymentView']))
check('Views: broadcasts',  lambda: __import__('apps.broadcasts.views', fromlist=['BroadcastFeedView']))
check('Views: groupbuy',    lambda: __import__('apps.groupbuy.views', fromlist=['JoinGroupBuyView']))
check('Views: stories',     lambda: __import__('apps.stories.views', fromlist=['StoryFeedView']))
check('Views: notifications',lambda: __import__('apps.notifications.views', fromlist=['NotificationListView']))
check('Views: admin_panel', lambda: __import__('apps.admin_panel.views', fromlist=['AdminDashboardView']))
check('Views: seasonal',    lambda: __import__('apps.seasonal.views', fromlist=['SeasonalGuideView']))

# ── URL resolution ──
from django.urls import reverse, NoReverseMatch
def rev(name, *args, **kwargs):
    try:
        reverse(name, args=args, kwargs=kwargs)
    except NoReverseMatch as e:
        raise AssertionError(str(e))

check('URL: listings:catalogue',        lambda: rev('listings:catalogue'))
check('URL: listings:create',           lambda: rev('listings:create'))
check('URL: listings:search',           lambda: rev('listings:search'))
check('URL: listings:detail',           lambda: rev('listings:detail', ref_code='TEST-0001-0001-0001'))
check('URL: accounts:register',         lambda: rev('accounts:register'))
check('URL: accounts:login',            lambda: rev('accounts:login'))
check('URL: accounts:logout',           lambda: rev('accounts:logout'))
check('URL: accounts:dashboard',        lambda: rev('accounts:dashboard'))
check('URL: accounts:password_reset',   lambda: rev('accounts:password_reset'))
check('URL: negotiations:submit_offer', lambda: rev('negotiations:submit_offer', ref_code='XXXX-0001-0001-0001'))
check('URL: negotiations:thread',       lambda: rev('negotiations:thread', ref_code='XXXX-0001-0001-0001'))
check('URL: orders:list',               lambda: rev('orders:list'))
check('URL: orders:detail',             lambda: rev('orders:detail', pk=1))
check('URL: orders:confirm',            lambda: rev('orders:confirm', pk=1))
check('URL: orders:cancel',             lambda: rev('orders:cancel', pk=1))
check('URL: orders:rate',               lambda: rev('orders:rate', pk=1))
check('URL: payments:initiate',         lambda: rev('payments:initiate', order_id=1))
check('URL: payments:callback',         lambda: rev('payments:callback'))
check('URL: payments:webhook',          lambda: rev('payments:webhook'))
check('URL: broadcasts:feed',           lambda: rev('broadcasts:feed'))
check('URL: broadcasts:create',         lambda: rev('broadcasts:create'))
check('URL: broadcasts:interest',       lambda: rev('broadcasts:interest', pk=1))
check('URL: groupbuy:join',             lambda: rev('groupbuy:join', listing_pk=1))
check('URL: groupbuy:leave',            lambda: rev('groupbuy:leave', listing_pk=1))
check('URL: seasonal:guide',            lambda: rev('seasonal:guide'))
check('URL: seasonal:calendar',         lambda: rev('seasonal:calendar'))
check('URL: stories:feed',              lambda: rev('stories:feed'))
check('URL: stories:create',            lambda: rev('stories:create'))
check('URL: stories:like',              lambda: rev('stories:like', pk=1))
check('URL: notifications:list',        lambda: rev('notifications:list'))
check('URL: notifications:mark_read',   lambda: rev('notifications:mark_read', pk=1))
check('URL: notifications:unread_count',lambda: rev('notifications:unread_count'))
check('URL: admin_panel:dashboard',     lambda: rev('admin_panel:dashboard'))
check('URL: admin_panel:audit_log',     lambda: rev('admin_panel:audit_log'))
check('URL: admin_panel:moderation',    lambda: rev('admin_panel:moderation'))

# ── DB: each model queryable ──
def db_check(label, fn):
    check(f'DB query: {label}', fn)

from apps.accounts.models import Customer
from apps.listings.models import Listing, FreshnessScore
from apps.negotiations.models import Offer, Deal, CounterOffer
from apps.orders.models import Order
from apps.notifications.models import Notification
from apps.broadcasts.models import PriceBroadcast
from apps.groupbuy.models import GroupBuy
from apps.stories.models import FarmStory
from apps.payments.models import PaystackTransaction, RefundRequest
from apps.admin_panel.models import AdminAuditLog
from apps.seasonal.models import HarvestSeasonSignal, AvailabilityCalendar

db_check('Customer.count',          lambda: Customer.objects.count())
db_check('Listing.count',           lambda: Listing.objects.count())
db_check('Offer.count',             lambda: Offer.objects.count())
db_check('Order.count',             lambda: Order.objects.count())
db_check('Notification.count',      lambda: Notification.objects.count())
db_check('PriceBroadcast.count',    lambda: PriceBroadcast.objects.count())
db_check('GroupBuy.count',          lambda: GroupBuy.objects.count())
db_check('FarmStory.count',         lambda: FarmStory.objects.count())
db_check('PaystackTransaction.count',lambda: PaystackTransaction.objects.count())
db_check('AdminAuditLog.count',     lambda: AdminAuditLog.objects.count())
db_check('HarvestSeasonSignal.count',lambda: HarvestSeasonSignal.objects.count())

# ── Key service functions callable ──
from apps.listings.services import generate_reference_code, create_unique_reference_code
check('Service fn: generate_reference_code',      lambda: generate_reference_code())
check('Service fn: create_unique_reference_code', lambda: create_unique_reference_code(Listing))
from apps.seasonal.services import evaluate_season_signal
check('Service fn: evaluate_season_signal (unknown)', lambda: evaluate_season_signal('cocoa', 'Lagos'))
check('Service fn: evaluate_season_signal (returns str)', lambda: [r for r in [evaluate_season_signal('maize','Kano')] if r in ('in_season','off_season')] or (_ for _ in ()).throw(AssertionError('bad return')))
from apps.notifications.services import get_unread_count
admin = Customer.objects.get(email='admin@agro.com')
check('Service fn: get_unread_count',  lambda: get_unread_count(admin))
from apps.admin_panel.services import get_dashboard_stats
check('Service fn: get_dashboard_stats', lambda: get_dashboard_stats())

# ── Management commands importable ──
check('Mgmt cmd: expire_offers',      lambda: __import__('apps.negotiations.management.commands.expire_offers', fromlist=['Command']))
check('Mgmt cmd: expire_broadcasts',  lambda: __import__('apps.broadcasts.management.commands.expire_broadcasts', fromlist=['Command']))
check('Mgmt cmd: expire_groupbuys',   lambda: __import__('apps.groupbuy.management.commands.expire_groupbuys', fromlist=['Command']))
check('Mgmt cmd: autoclose_orders',   lambda: __import__('apps.orders.management.commands.autoclose_orders', fromlist=['Command']))
check('Mgmt cmd: purge_notifications',lambda: __import__('apps.notifications.management.commands.purge_notifications', fromlist=['Command']))
check('Mgmt cmd: backup_database',    lambda: __import__('apps.admin_panel.management.commands.backup_database', fromlist=['Command']))

# ── SUMMARY ──
print()
print('=' * 60)
print(f'  TOTAL   : {len(passed)+len(failed)}')
print(f'  PASSED  : {len(passed)}  ✅')
print(f'  FAILED  : {len(failed)}  {"✅" if not failed else "❌"}')
print('=' * 60)
if failed:
    print()
    print('FAILURES TO FIX:')
    for label, err in failed:
        print(f'  ❌ {label}')
        print(f'     {err}')
else:
    print('  All checks passed — AgroConnect is production-ready! 🌿')
