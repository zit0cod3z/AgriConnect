from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Offer, CounterOffer, Deal


def submit_offer(customer, listing, price, quantity, message='') -> Offer:
    """Create an offer from a customer on a listing."""
    # Validate max 3 rounds per listing per customer
    existing = Offer.objects.filter(listing=listing, customer=customer).count()
    if existing >= 3:
        raise ValidationError('You have reached the maximum of 3 offers on this listing.')
    offer = Offer.objects.create(
        listing=listing,
        customer=customer,
        proposed_price=price,
        proposed_quantity=quantity,
        message=message,
        expires_at=timezone.now() + timezone.timedelta(hours=48),
    )
    # Notify farmer
    try:
        from apps.notifications.services import notify
        if listing.farmer:
            notify(
                customer=listing.farmer,
                event_type='new_offer',
                payload={'offer_id': offer.pk, 'listing_ref': listing.reference_code},
            )
    except Exception:
        pass
    return offer


def submit_counter_offer(listing, offer, new_price, message='') -> CounterOffer:
    """Create a counter-offer from the farmer."""
    count = offer.counter_offers.count()
    if count >= 3:
        raise ValidationError('Maximum 3 counter-offer rounds reached.')
    co = CounterOffer.objects.create(offer=offer, proposed_price=new_price, message=message)
    offer.status = 'countered'
    offer.save(update_fields=['status'])
    # Notify customer
    try:
        from apps.notifications.services import notify
        notify(
            customer=offer.customer,
            event_type='counter_offer',
            payload={'counter_offer_id': co.pk, 'offer_id': offer.pk},
        )
    except Exception:
        pass
    return co


@transaction.atomic
def accept_offer(offer: Offer) -> Deal:
    """Accept an offer and create a Deal + Order."""
    deal = Deal.objects.create(
        offer=offer,
        agreed_price=offer.proposed_price,
        agreed_quantity=offer.proposed_quantity,
    )
    offer.status = 'accepted'
    offer.save(update_fields=['status'])

    # Reduce listing quantity
    listing = offer.listing
    listing.quantity = listing.quantity - offer.proposed_quantity
    if listing.quantity < 0:
        listing.quantity = 0
    listing.save(update_fields=['quantity'])

    # Notify customer
    try:
        from apps.notifications.services import notify
        notify(
            customer=offer.customer,
            event_type='deal_accepted',
            payload={'deal_id': deal.pk, 'listing_ref': listing.reference_code},
        )
    except Exception:
        pass

    # Create order
    try:
        from apps.orders.services import create_order_from_deal
        create_order_from_deal(deal)
    except Exception:
        pass

    return deal


@transaction.atomic
def accept_counter_offer(counter_offer: CounterOffer) -> Deal:
    """Accept a counter-offer (customer accepts farmer's price)."""
    counter_offer.status = 'accepted'
    counter_offer.save(update_fields=['status'])
    offer = counter_offer.offer
    offer.proposed_price = counter_offer.proposed_price
    offer.save(update_fields=['proposed_price'])
    return accept_offer(offer)


def reject_offer(offer: Offer) -> None:
    """Reject an offer."""
    offer.status = 'rejected'
    offer.save(update_fields=['status'])
    try:
        from apps.notifications.services import notify
        notify(
            customer=offer.customer,
            event_type='counter_offer',
            payload={'offer_id': offer.pk, 'action': 'rejected'},
        )
    except Exception:
        pass


def get_negotiation_thread(listing, customer) -> list:
    """Return chronological list of offers and counter-offers."""
    thread = []
    offers = Offer.objects.filter(listing=listing, customer=customer).prefetch_related('counter_offers')
    for offer in offers:
        thread.append({
            'type': 'offer', 'actor': 'customer',
            'price': offer.proposed_price, 'quantity': offer.proposed_quantity,
            'message': offer.message, 'status': offer.status, 'timestamp': offer.created_at,
            'id': offer.pk,
        })
        for co in offer.counter_offers.all():
            thread.append({
                'type': 'counter_offer', 'actor': 'farmer',
                'price': co.proposed_price, 'quantity': offer.proposed_quantity,
                'message': co.message, 'status': co.status, 'timestamp': co.created_at,
                'id': co.pk,
            })
    thread.sort(key=lambda x: x['timestamp'])
    return thread


def expire_stale_offers() -> int:
    """Expire all pending offers past their expiry date."""
    stale = Offer.objects.filter(status='pending', expires_at__lt=timezone.now())
    count = stale.count()
    for offer in stale:
        offer.status = 'expired'
        offer.save(update_fields=['status'])
        try:
            from apps.notifications.services import notify
            notify(
                customer=offer.customer,
                event_type='counter_offer',
                payload={'offer_id': offer.pk, 'action': 'expired'},
            )
        except Exception:
            pass
    return count
