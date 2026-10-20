from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import PriceBroadcast, BroadcastInterest


def create_broadcast(data: dict) -> PriceBroadcast:
    """Create a price broadcast."""
    from apps.listings.services import create_unique_reference_code
    ref = create_unique_reference_code(PriceBroadcast)
    broadcast = PriceBroadcast.objects.create(
        reference_code=ref,
        broadcaster_name=data['broadcaster_name'],
        broadcaster_phone=data['broadcaster_phone'],
        broadcaster_customer=data.get('broadcaster_customer'),
        produce_name=data['produce_name'],
        category=data.get('category', ''),
        offered_price=data['offered_price'],
        quantity_wanted=data['quantity_wanted'],
        unit=data.get('unit', 'kg'),
        state=data.get('state', ''),
        message=data.get('message', ''),
        expires_at=data['expires_at'],
    )
    return broadcast


def get_active_broadcasts():
    """Return all non-expired broadcasts."""
    return PriceBroadcast.objects.filter(is_expired=False, expires_at__gt=timezone.now())


def record_interest(broadcast: PriceBroadcast, responder_name: str, responder_phone: str,
                    message: str = '', customer=None) -> BroadcastInterest:
    """Record interest in a broadcast."""
    if BroadcastInterest.objects.filter(broadcast=broadcast, responder_phone=responder_phone).exists():
        raise ValidationError('You have already expressed interest in this broadcast.')
    interest = BroadcastInterest.objects.create(
        broadcast=broadcast,
        responder_name=responder_name,
        responder_phone=responder_phone,
        responder_customer=customer,
        message=message,
    )
    # Notify broadcaster if registered
    if broadcast.broadcaster_customer:
        try:
            from apps.notifications.services import notify
            notify(
                customer=broadcast.broadcaster_customer,
                event_type='broadcast_interest',
                payload={'broadcast_id': broadcast.pk, 'interest_id': interest.pk},
            )
        except Exception:
            pass
    return interest


def expire_stale_broadcasts() -> int:
    """Expire broadcasts past their expiry date."""
    stale = PriceBroadcast.objects.filter(is_expired=False, expires_at__lt=timezone.now())
    count = stale.count()
    stale.update(is_expired=True)
    return count
