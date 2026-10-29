from django.db import models

ORDER_STATUS = [
    ('pending_confirmation', 'Pending Confirmation'),   # waiting for farmer to accept
    ('accepted',             'Accepted by Farmer'),     # farmer accepted — awaiting buyer payment choice
    ('awaiting_address',     'Awaiting Address'),        # buyer needs to provide delivery address
    ('pending_payment',      'Pending Payment'),         # Paystack payment initiated
    ('confirmed',            'Confirmed'),               # payment confirmed / POD confirmed
    ('ready',                'Ready'),                   # farmer packed
    ('in_transit',           'In Transit'),              # farmer dispatched
    ('delivered',            'Delivered'),               # buyer received
    ('cancelled',            'Cancelled'),
    ('closed',               'Closed'),
]

DELIVERY_METHOD = [
    ('pod',      'Payment on Delivery'),
    ('paystack', 'Online Payment (Paystack)'),
    ('pickup',   'Store / Farm Pickup'),
]


class Order(models.Model):
    deal            = models.OneToOneField('negotiations.Deal', on_delete=models.PROTECT, related_name='order')
    customer        = models.ForeignKey('accounts.Customer', on_delete=models.PROTECT, related_name='orders')
    status          = models.CharField(max_length=30, choices=ORDER_STATUS, default='pending_confirmation')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD, default='pod')
    farmer_phone    = models.CharField(max_length=20)

    # Addresses
    delivery_address = models.TextField(blank=True, help_text='Buyer delivery address (POD)')
    pickup_address   = models.TextField(blank=True, help_text='Farmer store/farm pickup address')

    # Coordinates (auto-populated when address set)
    delivery_lat = models.FloatField(null=True, blank=True)
    delivery_lng = models.FloatField(null=True, blank=True)
    pickup_lat   = models.FloatField(null=True, blank=True)
    pickup_lng   = models.FloatField(null=True, blank=True)

    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders_order'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.pk} [{self.status}]"
