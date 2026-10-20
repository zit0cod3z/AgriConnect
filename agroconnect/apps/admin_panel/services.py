from .models import AdminAuditLog


def log_admin_action(admin_user, entity_type: str, entity_id: str, action: str, detail: str = '') -> AdminAuditLog:
    """Create an immutable audit log entry. Never updates or deletes existing records."""
    return AdminAuditLog.objects.create(
        admin_user=admin_user,
        entity_type=entity_type,
        entity_id=str(entity_id),
        action=action,
        detail=detail,
    )


def get_dashboard_stats() -> dict:
    """Return KPI stats for the admin dashboard."""
    from apps.listings.models import Listing
    from apps.accounts.models import Customer
    from apps.orders.models import Order
    from apps.groupbuy.models import GroupBuy
    from apps.broadcasts.models import PriceBroadcast
    from django.utils import timezone

    return {
        'active_listings': Listing.objects.filter(is_active=True).count(),
        'total_customers': Customer.objects.count(),
        'orders_by_status': {
            status: Order.objects.filter(status=status).count()
            for status, _ in Order._meta.get_field('status').choices
        },
        'groupbuys_in_progress': GroupBuy.objects.filter(is_active=True, threshold_reached=False).count(),
        'active_broadcasts': PriceBroadcast.objects.filter(is_expired=False, expires_at__gt=timezone.now()).count(),
    }


def get_payment_summary_stats() -> dict:
    """Return payment KPI stats."""
    from apps.orders.models import Order
    from apps.payments.models import PaystackTransaction, RefundRequest

    return {
        'paystack_orders': Order.objects.filter(delivery_method='paystack').count(),
        'pod_orders': Order.objects.filter(delivery_method='pod').count(),
        'pending_refunds': RefundRequest.objects.filter(status='pending').count(),
        'total_success_kobo': sum(
            t.amount_kobo for t in PaystackTransaction.objects.filter(paystack_status='success')
        ),
    }
