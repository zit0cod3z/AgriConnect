from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Order


@transaction.atomic
def create_order_from_deal(deal) -> Order:
    """Create an Order from a negotiated Deal."""
    order = Order.objects.create(
        deal=deal,
        customer=deal.offer.customer,
        farmer_phone=deal.offer.listing.contact_phone,
        status='pending_confirmation',
    )
    return order


def confirm_order(order: Order) -> Order:
    """Confirm an order (farmer or customer action)."""
    if order.status != 'pending_confirmation':
        raise ValidationError('Order cannot be confirmed from its current status.')
    order.status = 'confirmed'
    order.save(update_fields=['status', 'updated_at'])
    _notify_order_change(order)
    return order


def mark_in_transit(order: Order) -> Order:
    """Mark order as in transit."""
    if order.status not in ('confirmed', 'ready'):
        raise ValidationError('Order must be confirmed or ready before marking in transit.')
    order.status = 'in_transit'
    order.save(update_fields=['status', 'updated_at'])
    _notify_order_change(order)
    return order


def mark_delivered(order: Order) -> Order:
    """Mark order as delivered."""
    if order.status != 'in_transit':
        raise ValidationError('Order must be in transit before marking as delivered.')
    order.status = 'delivered'
    order.save(update_fields=['status', 'updated_at'])
    _notify_order_change(order)
    return order


def cancel_order(order: Order) -> Order:
    """Cancel an order. In-transit orders create a cancellation request instead."""
    if order.status == 'in_transit':
        # Create cancellation request notification only
        try:
            from apps.notifications.services import notify
            if order.deal.offer.listing.farmer:
                notify(
                    customer=order.deal.offer.listing.farmer,
                    event_type='order_status_change',
                    payload={'order_id': order.pk, 'action': 'cancellation_request'},
                )
        except Exception:
            pass
        return order
    if order.status not in ('pending_confirmation', 'confirmed', 'ready', 'pending_payment'):
        raise ValidationError('Order cannot be cancelled from its current status.')
    order.status = 'cancelled'
    order.save(update_fields=['status', 'updated_at'])
    _notify_order_change(order)
    return order


def auto_close_stale_orders() -> int:
    """Close orders stuck at delivered for more than 7 days."""
    threshold = timezone.now() - timedelta(days=7)
    stale = Order.objects.filter(status='delivered', updated_at__lt=threshold)
    count = stale.count()
    stale.update(status='closed', updated_at=timezone.now())
    return count


def submit_freshness_score(order, customer, stars: int, review_text: str = ''):
    """Submit a freshness score for a delivered order."""
    from apps.listings.models import FreshnessScore
    if FreshnessScore.objects.filter(order=order).exists():
        raise ValidationError('A freshness score has already been submitted for this order.')
    score = FreshnessScore.objects.create(
        order=order,
        customer=customer,
        farmer_phone=order.farmer_phone,
        stars=stars,
        review_text=review_text,
    )
    return score


def _notify_order_change(order: Order):
    """Helper to fire order status change notification."""
    try:
        from apps.notifications.services import notify
        notify(
            customer=order.customer,
            event_type='order_status_change',
            payload={'order_id': order.pk, 'status': order.status},
        )
    except Exception:
        pass
