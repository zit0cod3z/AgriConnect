from django.contrib import admin
from .models import DeliveryTracking


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ('order', 'delivery_type', 'status', 'farmer_address', 'buyer_address', 'last_updated')
    list_filter  = ('status', 'delivery_type')
    readonly_fields = ('created_at', 'last_updated')
