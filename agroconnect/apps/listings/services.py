import hmac
import secrets
import string
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.core.exceptions import ValidationError
from .models import Listing, FreshnessScore

ALPHABET = string.ascii_uppercase + string.digits


def generate_reference_code():
    raw = ''.join(secrets.choice(ALPHABET) for _ in range(16))
    return f"{raw[0:4]}-{raw[4:8]}-{raw[8:12]}-{raw[12:16]}"


def create_unique_reference_code(model_class=None):
    if model_class is None:
        model_class = Listing
    for _ in range(10):
        code = generate_reference_code()
        if not model_class.objects.filter(reference_code=code).exists():
            return code
    raise RuntimeError("Could not generate unique reference code")


def verify_listing_access(reference_code, phone):
    try:
        listing = Listing.objects.get(reference_code=reference_code, is_active=True)
    except Listing.DoesNotExist:
        hmac.compare_digest("dummy_phone", str(phone))
        return None
    if hmac.compare_digest(str(listing.contact_phone), str(phone)):
        return listing
    return None


def create_listing(data, images=None):
    required = ['produce_name', 'category', 'quantity', 'unit', 'price_per_unit', 'farm_state', 'farm_lga', 'contact_phone']
    errors = {}
    for field in required:
        if not data.get(field):
            errors[field] = f'{field.replace("_", " ").title()} is required.'
    if errors:
        raise ValidationError(errors)
    listing = Listing.objects.create(
        reference_code=create_unique_reference_code(),
        produce_name=data['produce_name'],
        category=data['category'],
        quantity=data['quantity'],
        unit=data['unit'],
        price_per_unit=data['price_per_unit'],
        farm_state=data['farm_state'],
        farm_lga=data['farm_lga'],
        contact_phone=data['contact_phone'],
        description=data.get('description', ''),
        group_buy_eligible=data.get('group_buy_eligible', False),
        group_buy_threshold_qty=data.get('group_buy_threshold_qty'),
        group_buy_bulk_price=data.get('group_buy_bulk_price'),
        farmer=data.get('farmer'),
    )
    return listing


def get_catalogue(filters=None, page=1):
    qs = Listing.objects.filter(is_active=True)
    if filters:
        if filters.get('category'):
            qs = qs.filter(category=filters['category'])
        if filters.get('farm_state'):
            qs = qs.filter(farm_state__icontains=filters['farm_state'])
        if filters.get('price_min'):
            qs = qs.filter(price_per_unit__gte=filters['price_min'])
        if filters.get('price_max'):
            qs = qs.filter(price_per_unit__lte=filters['price_max'])
    paginator = Paginator(qs, 20)
    return paginator.get_page(page)


def search_listings(query, filters=None):
    qs = Listing.objects.filter(
        is_active=True
    ).filter(
        Q(produce_name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__icontains=query)
    )
    return qs


def deactivate_listing(listing):
    listing.is_active = False
    listing.save(update_fields=['is_active'])


def get_farmer_freshness_score(farmer_phone):
    result = FreshnessScore.objects.filter(farmer_phone=farmer_phone).aggregate(
        average=Avg('stars'), count=Count('id')
    )
    count = result['count'] or 0
    if count < 3:
        return {'average': None, 'count': count, 'display': 'Not yet rated'}
    avg = round(result['average'], 1)
    return {'average': avg, 'count': count, 'display': f"{avg} ★ ({count} ratings)"}
