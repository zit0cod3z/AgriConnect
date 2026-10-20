from django.db import models


class GroupBuy(models.Model):
    listing = models.OneToOneField('listings.Listing', on_delete=models.CASCADE, related_name='group_buy')
    threshold_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    current_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bulk_price = models.DecimalField(max_digits=10, decimal_places=2)
    threshold_reached = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'groupbuy_group_buy'

    def __str__(self):
        return f"GroupBuy for {self.listing}"


class GroupBuyParticipant(models.Model):
    group_buy = models.ForeignKey(GroupBuy, on_delete=models.CASCADE, related_name='participants')
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, related_name='group_buy_participations')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'groupbuy_participant'
        unique_together = [('group_buy', 'customer')]

    def __str__(self):
        return f"{self.customer} in {self.group_buy}"
