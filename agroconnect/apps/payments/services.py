import hashlib
import hmac
import os
import uuid
import requests
from django.core.exceptions import ValidationError
from .models import PaystackTransaction, RefundRequest

PAYSTACK_BASE = 'https://api.paystack.co'


def _secret_key():
    key = os.environ.get('PAYSTACK_SECRET_KEY', '')
    if not key:
        raise ValidationError('PAYSTACK_SECRET_KEY is not configured.')
    return key


def initiate_paystack_payment(order) -> str:
    """Initialise a Paystack transaction. Returns the authorisation_url."""
    secret = _secret_key()
    reference = f"AGRO-{order.pk}-{uuid.uuid4().hex[:8].upper()}"
    amount_kobo = int(order.deal.agreed_price * 100)

    txn = PaystackTransaction.objects.create(
        order=order,
        reference=reference,
        amount_kobo=amount_kobo,
        paystack_status='initiated',
    )

    from django.conf import settings
    callback_url = getattr(settings, 'PAYSTACK_CALLBACK_URL', 'http://localhost:8000/payments/callback/')

    resp = requests.post(
        f'{PAYSTACK_BASE}/transaction/initialize',
        json={
            'email': order.customer.email,
            'amount': amount_kobo,
            'reference': reference,
            'callback_url': callback_url,
        },
        headers={'Authorization': f'Bearer {secret}'},
        timeout=15,
    )
    data = resp.json()
    if data.get('status'):
        auth_url = data['data']['authorization_url']
        txn.authorisation_url = auth_url
        txn.paystack_response = data
        txn.save(update_fields=['authorisation_url', 'paystack_response'])
        order.delivery_method = 'paystack'
        order.status = 'pending_payment'
        order.save(update_fields=['delivery_method', 'status'])
        return auth_url
    raise ValidationError(data.get('message', 'Paystack initialisation failed.'))


def verify_paystack_payment(reference: str) -> dict:
    """Verify a Paystack transaction by reference. Returns the response data dict."""
    secret = _secret_key()
    resp = requests.get(
        f'{PAYSTACK_BASE}/transaction/verify/{reference}',
        headers={'Authorization': f'Bearer {secret}'},
        timeout=15,
    )
    return resp.json()


def handle_paystack_webhook(payload: dict, signature: str) -> bool:
    """Validate webhook signature and process event. Idempotent."""
    secret = _secret_key()
    import json
    raw_body = json.dumps(payload, separators=(',', ':')).encode()
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha512).hexdigest()  # type: ignore

    if not hmac.compare_digest(expected, signature):
        return False

    event = payload.get('event', '')
    data = payload.get('data', {})
    reference = data.get('reference', '')

    try:
        txn = PaystackTransaction.objects.get(reference=reference)
    except PaystackTransaction.DoesNotExist:
        return True  # Unknown ref — ignore gracefully

    # Idempotency: skip terminal statuses
    if txn.paystack_status in ('success', 'failed'):
        return True

    if event == 'charge.success':
        txn.paystack_status = 'success'
        txn.paystack_response = data
        txn.save(update_fields=['paystack_status', 'paystack_response'])
        from apps.orders.services import confirm_order
        try:
            confirm_order(txn.order)
        except Exception:
            pass
    elif event in ('transfer.failed', 'charge.failed'):
        txn.paystack_status = 'failed'
        txn.save(update_fields=['paystack_status'])
        txn.order.status = 'pending_payment'
        txn.order.save(update_fields=['status'])

    return True


def record_refund_request(order, customer, reason: str) -> RefundRequest:
    """Record a refund request and notify admin."""
    refund = RefundRequest.objects.create(order=order, customer=customer, reason=reason)
    try:
        from apps.notifications.services import notify
        from apps.accounts.models import Customer
        admins = Customer.objects.filter(is_staff=True)
        for admin in admins:
            notify(
                customer=admin,
                event_type='payment_failed',
                payload={'refund_request_id': refund.pk, 'order_id': order.pk},
            )
    except Exception:
        pass
    return refund


def get_payment_summary_stats() -> dict:
    from apps.orders.models import Order
    return {
        'paystack_orders': Order.objects.filter(delivery_method='paystack').count(),
        'pod_orders': Order.objects.filter(delivery_method='pod').count(),
        'pending_refunds': RefundRequest.objects.filter(status='pending').count(),
        'total_success_kobo': sum(
            t.amount_kobo for t in PaystackTransaction.objects.filter(paystack_status='success')
        ),
    }
