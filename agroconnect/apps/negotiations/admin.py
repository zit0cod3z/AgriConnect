from django.contrib import admin
from .models import Offer, CounterOffer, Deal


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('pk', 'listing', 'customer', 'proposed_price', 'status', 'expires_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('listing__produce_name', 'customer__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CounterOffer)
class CounterOfferAdmin(admin.ModelAdmin):
    list_display = ('pk', 'offer', 'proposed_price', 'status', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('pk', 'offer', 'agreed_price', 'agreed_quantity', 'created_at')
    readonly_fields = ('created_at',)
