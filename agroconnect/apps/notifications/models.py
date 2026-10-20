from django.db import models

EVENT_TYPES = [
    ('new_offer', 'New Offer Received'),
    ('counter_offer', 'Counter-Offer Received'),
    ('deal_accepted', 'Deal Accepted'),
    ('order_status_change', 'Order Status Changed'),
    ('group_buy_threshold', 'Group-Buy Threshold Reached'),
    ('group_buy_expiry_warning', 'Group-Buy Expiry Warning'),
    ('broadcast_interest', 'Broadcast Interest Received'),
    ('freshness_score_received', 'Freshness Score Received'),
    ('payment_confirmed', 'Payment Confirmed'),
    ('payment_failed', 'Payment Failed'),
]


class Notification(models.Model):
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, related_name='notifications')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    payload = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} for {self.customer}"
