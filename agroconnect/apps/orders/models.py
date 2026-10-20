from django.db import models

ORDER_STATUS = [
    ('pending_payment', 'Pending Payment'),
    ('pending_confirmation', 'Pending Confirmation'),
    ('confirmed', 'Confirmed'),
    ('ready', 'Ready'),
    ('in_transit', 'In Transit'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
    ('closed', 'Closed'),
]

DELIVERY_METHOD = [
    ('pod', 'Payment on Delivery'),
    ('paystack', 'Online Payment (Paystack)'),
]


class Order(models.Model):
    deal = models.OneToOneField('negotiations.Deal', on_delete=models.PROTECT, related_name='order')
    customer = models.ForeignKey('accounts.Customer', on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=30, choices=ORDER_STATUS, default='pending_confirmation')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD, default='pod')
    farmer_phone = models.CharField(max_length=20)
    delivery_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders_order'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.pk} [{self.status}]"
