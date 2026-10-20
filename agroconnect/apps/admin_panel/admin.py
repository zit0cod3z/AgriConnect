from django.contrib import admin
from .models import AdminAuditLog


@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ('admin_user', 'entity_type', 'entity_id', 'action', 'timestamp')
    list_filter = ('entity_type', 'action')
    search_fields = ('admin_user__email', 'detail')
    readonly_fields = ('admin_user', 'entity_type', 'entity_id', 'action', 'detail', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
