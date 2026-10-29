from django.db import models

DELIVERY_TYPE_CHOICES = [
    ('delivery', 'Farmer Delivers to Buyer'),
    ('pickup',   'Buyer Picks Up from Farm'),
]

TRACKING_STATUS = [
    ('pending',     'Pending'),
    ('active',      'Active'),
    ('arrived',     'Arrived'),
    ('completed',   'Completed'),
    ('cancelled',   'Cancelled'),
]


class DeliveryTracking(models.Model):
    """Stores a live delivery/pickup session for an order."""
    order = models.OneToOneField(
        'orders.Order', on_delete=models.CASCADE, related_name='delivery_tracking'
    )
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPE_CHOICES, default='delivery')
    status = models.CharField(max_length=20, choices=TRACKING_STATUS, default='pending')

    # Farmer location (farm / origin)
    farmer_lat  = models.FloatField(null=True, blank=True)
    farmer_lng  = models.FloatField(null=True, blank=True)
    farmer_address = models.TextField(blank=True)

    # Buyer location (delivery destination)
    buyer_lat   = models.FloatField(null=True, blank=True)
    buyer_lng   = models.FloatField(null=True, blank=True)
    buyer_address = models.TextField(blank=True)

    # Live courier/farmer current position (updated via AJAX)
    current_lat = models.FloatField(null=True, blank=True)
    current_lng = models.FloatField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    estimated_arrival = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'delivery_tracking'

    def __str__(self):
        return f"Tracking Order #{self.order_id} [{self.status}]"
