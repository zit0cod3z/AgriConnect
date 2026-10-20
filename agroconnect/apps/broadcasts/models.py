from django.db import models


class PriceBroadcast(models.Model):
    reference_code = models.CharField(max_length=19, unique=True, db_index=True)
    broadcaster_name = models.CharField(max_length=200)
    broadcaster_phone = models.CharField(max_length=20)
    broadcaster_customer = models.ForeignKey(
        'accounts.Customer', null=True, blank=True, on_delete=models.SET_NULL, related_name='broadcasts'
    )
    produce_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    offered_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_wanted = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=30)
    state = models.CharField(max_length=50)
    message = models.TextField(blank=True)
    is_expired = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'broadcasts_price_broadcast'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.produce_name} @ {self.offered_price} by {self.broadcaster_name}"


class BroadcastInterest(models.Model):
    broadcast = models.ForeignKey(PriceBroadcast, on_delete=models.CASCADE, related_name='interests')
    responder_name = models.CharField(max_length=200)
    responder_phone = models.CharField(max_length=20)
    responder_customer = models.ForeignKey(
        'accounts.Customer', null=True, blank=True, on_delete=models.SET_NULL, related_name='broadcast_interests'
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'broadcasts_interest'
        unique_together = [('broadcast', 'responder_phone')]
        ordering = ['-created_at']

    def __str__(self):
        return f"Interest by {self.responder_name} on {self.broadcast}"
