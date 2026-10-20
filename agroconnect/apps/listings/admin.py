from django.contrib import admin
from .models import Listing, ListingImage, FreshnessScore


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('produce_name', 'category', 'farm_state', 'price_per_unit', 'quantity', 'unit', 'is_active', 'created_at')
    list_filter = ('category', 'farm_state', 'is_active', 'is_flagged')
    search_fields = ('produce_name', 'contact_phone', 'reference_code')
    readonly_fields = ('reference_code', 'created_at', 'updated_at')


@admin.register(FreshnessScore)
class FreshnessScoreAdmin(admin.ModelAdmin):
    list_display = ('farmer_phone', 'stars', 'customer', 'created_at')
    list_filter = ('stars', 'is_flagged')
