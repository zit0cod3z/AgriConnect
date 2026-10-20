from django.contrib import admin
from .models import PaystackTransaction, RefundRequest


@admin.register(PaystackTransaction)
class PaystackTransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'order', 'amount_kobo', 'paystack_status', 'created_at')
    list_filter = ('paystack_status',)
    search_fields = ('reference',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ('pk', 'order', 'customer', 'status', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('created_at', 'updated_at')
