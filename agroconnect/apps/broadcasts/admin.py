from django.contrib import admin
from .models import PriceBroadcast, BroadcastInterest


@admin.register(PriceBroadcast)
class PriceBroadcastAdmin(admin.ModelAdmin):
    list_display = ('produce_name', 'broadcaster_name', 'offered_price', 'is_expired', 'expires_at', 'created_at')
    list_filter = ('is_expired',)
    search_fields = ('produce_name', 'broadcaster_name')


@admin.register(BroadcastInterest)
class BroadcastInterestAdmin(admin.ModelAdmin):
    list_display = ('broadcast', 'responder_name', 'responder_phone', 'created_at')
