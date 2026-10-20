from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'customer', 'status', 'delivery_method', 'farmer_phone', 'created_at')
    list_filter = ('status', 'delivery_method')
    search_fields = ('customer__email', 'farmer_phone')
    readonly_fields = ('created_at', 'updated_at')
