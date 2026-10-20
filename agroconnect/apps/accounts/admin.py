from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'state', 'email_verified', 'is_locked', 'date_joined')
    list_filter = ('email_verified', 'is_locked', 'state')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('AgroConnect', {'fields': ('phone', 'state', 'email_verified', 'is_locked', 'locked_until', 'failed_login_attempts')}),
    )
