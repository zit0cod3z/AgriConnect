from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from .models import GroupBuy, GroupBuyParticipant


@transaction.atomic
def join_group_buy(group_buy: GroupBuy, customer, quantity) -> GroupBuyParticipant:
    """Join a group buy."""
    if not group_buy.is_active:
        raise ValidationError('This group buy is no longer active.')
    if GroupBuyParticipant.objects.filter(group_buy=group_buy, customer=customer).exists():
        raise ValidationError('You have already joined this group buy.')

    participant = GroupBuyParticipant.objects.create(
        group_buy=group_buy, customer=customer, quantity=quantity
    )

    GroupBuy.objects.filter(pk=group_buy.pk).update(
        current_quantity=F('current_quantity') + quantity
    )
    group_buy.refresh_from_db()

    if not group_buy.threshold_reached and group_buy.current_quantity >= group_buy.threshold_quantity:
        GroupBuy.objects.filter(pk=group_buy.pk).update(threshold_reached=True)
        group_buy.refresh_from_db()
        _apply_bulk_price_to_all(group_buy)
        _notify_all_participants(group_buy)

    return participant


def leave_group_buy(group_buy: GroupBuy, customer) -> None:
    """Leave a group buy."""
    try:
        participant = GroupBuyParticipant.objects.get(group_buy=group_buy, customer=customer, is_active=True)
    except GroupBuyParticipant.DoesNotExist:
        raise ValidationError('You are not an active participant in this group buy.')
    GroupBuy.objects.filter(pk=group_buy.pk).update(
        current_quantity=F('current_quantity') - participant.quantity
    )
    participant.is_active = False
    participant.save(update_fields=['is_active'])


def get_group_buy_progress(group_buy: GroupBuy) -> dict:
    """Return group buy progress stats."""
    current = float(group_buy.current_quantity)
    threshold = float(group_buy.threshold_quantity)
    progress_percent = min(100.0, (current / threshold * 100)) if threshold > 0 else 0.0
    participant_count = group_buy.participants.filter(is_active=True).count()
    return {
        'progress_percent': progress_percent,
        'current_quantity': current,
        'quantity_remaining': max(0.0, threshold - current),
        'participant_count': participant_count,
        'threshold_reached': group_buy.threshold_reached,
    }


def expire_stale_groupbuys() -> int:
    """Expire group buys past their expiry without reaching threshold."""
    now = timezone.now()
    stale = GroupBuy.objects.filter(is_active=True, expires_at__lt=now, threshold_reached=False)
    count = stale.count()
    for gb in stale:
        gb.is_active = False
        gb.save(update_fields=['is_active'])
        for participant in gb.participants.filter(is_active=True):
            try:
                from apps.notifications.services import notify
                notify(
                    customer=participant.customer,
                    event_type='group_buy_expiry_warning',
                    payload={'group_buy_id': gb.pk, 'listing_id': gb.listing_id},
                )
            except Exception:
                pass
    return count


def _apply_bulk_price_to_all(group_buy: GroupBuy):
    """Apply bulk price to the listing."""
    listing = group_buy.listing
    listing.price_per_unit = group_buy.bulk_price
    listing.save(update_fields=['price_per_unit'])


def _notify_all_participants(group_buy: GroupBuy):
    """Notify all participants the threshold has been reached."""
    for participant in group_buy.participants.filter(is_active=True):
        try:
            from apps.notifications.services import notify
            notify(
                customer=participant.customer,
                event_type='group_buy_threshold',
                payload={'group_buy_id': group_buy.pk, 'bulk_price': str(group_buy.bulk_price)},
            )
        except Exception:
            pass
