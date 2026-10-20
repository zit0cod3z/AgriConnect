from django.db import models
from django.utils import timezone
from datetime import timedelta


OFFER_STATUS = [
    ('pending', 'Pending'),
    ('countered', 'Countered'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
    ('expired', 'Expired'),
]

COUNTER_OFFER_STATUS = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]


class Offer(models.Model):
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='offers')
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, related_name='offers')
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    proposed_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=OFFER_STATUS, default='pending')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'negotiations_offer'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.pk and not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=48)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Offer by {self.customer} on {self.listing}"


class CounterOffer(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='counter_offers')
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=COUNTER_OFFER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'negotiations_counter_offer'
        ordering = ['created_at']

    def __str__(self):
        return f"CounterOffer on {self.offer}"


class Deal(models.Model):
    offer = models.OneToOneField(Offer, on_delete=models.CASCADE, related_name='deal')
    agreed_price = models.DecimalField(max_digits=10, decimal_places=2)
    agreed_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'negotiations_deal'

    def __str__(self):
        return f"Deal: {self.agreed_quantity} @ {self.agreed_price}"
