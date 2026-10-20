from django.contrib import admin
from .models import GroupBuy, GroupBuyParticipant


@admin.register(GroupBuy)
class GroupBuyAdmin(admin.ModelAdmin):
    list_display = ('listing', 'current_quantity', 'threshold_quantity', 'threshold_reached', 'is_active', 'expires_at')
    list_filter = ('threshold_reached', 'is_active')


@admin.register(GroupBuyParticipant)
class GroupBuyParticipantAdmin(admin.ModelAdmin):
    list_display = ('group_buy', 'customer', 'quantity', 'is_active', 'joined_at')
    list_filter = ('is_active',)
