from django.db import models


class AdminAuditLog(models.Model):
    admin_user = models.ForeignKey('accounts.Customer', on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    detail = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_panel_audit_log'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.admin_user} {self.action} {self.entity_type}#{self.entity_id}"
