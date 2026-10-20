from django.utils import timezone
from datetime import timedelta
from .models import Notification
from .sms import SMSAdapter

SMS_EVENTS = {'new_offer', 'deal_accepted', 'order_status_change'}
sms = SMSAdapter()


def notify(customer, event_type, payload=None):
    if payload is None:
        payload = {}
    notif = Notification.objects.create(customer=customer, event_type=event_type, payload=payload)
    if event_type in SMS_EVENTS and hasattr(customer, 'phone') and customer.phone:
        msg = _build_sms(event_type, payload)
        if msg:
            sms.send(customer.phone, msg)
    return notif


def _build_sms(event_type, payload):
    msgs = {
        'new_offer': f"AgroConnect: New offer of ₦{payload.get('price', '?')} received. Log in to respond.",
        'deal_accepted': f"AgroConnect: Your deal is confirmed. Order #{payload.get('order_id', '?')} created.",
        'order_status_change': f"AgroConnect: Order #{payload.get('order_id', '?')} status: {payload.get('status', '?')}.",
    }
    return msgs.get(event_type)


def mark_read(notification):
    notification.is_read = True
    notification.save(update_fields=['is_read'])


def get_unread_count(user):
    return Notification.objects.filter(customer=user, is_read=False).count()


def purge_old_notifications():
    cutoff = timezone.now() - timedelta(days=90)
    deleted, _ = Notification.objects.filter(is_read=True, created_at__lt=cutoff).delete()
    return deleted
