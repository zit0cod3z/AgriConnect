from django.db import models

CATEGORY_CHOICES = [
    ('grains', 'Grains'), ('tubers', 'Tubers'), ('vegetables', 'Vegetables'),
    ('spices', 'Spices'), ('fruits', 'Fruits'), ('legumes', 'Legumes'), ('other', 'Other'),
]


class Listing(models.Model):
    reference_code = models.CharField(max_length=19, unique=True, db_index=True)
    produce_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=30)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    farm_state = models.CharField(max_length=50)
    farm_lga = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    group_buy_eligible = models.BooleanField(default=False)
    group_buy_threshold_qty = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    group_buy_bulk_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    farmer = models.ForeignKey('accounts.Customer', null=True, blank=True, on_delete=models.SET_NULL, related_name='listings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'listings_listing'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.produce_name} ({self.farm_state})"


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listings/%Y/%m/')
    is_farm_story_photo = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'listings_image'


class FreshnessScore(models.Model):
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='freshness_score')
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE)
    farmer_phone = models.CharField(max_length=20, db_index=True)
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField(blank=True)
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'listings_freshness_score'
