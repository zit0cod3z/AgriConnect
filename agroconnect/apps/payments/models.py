from django.db import models

PAYSTACK_STATUS = [
    ('initiated', 'Initiated'),
    ('success', 'Success'),
    ('failed', 'Failed'),
    ('abandoned', 'Abandoned'),
]

REFUND_STATUS = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('processed', 'Processed'),
]


class PaystackTransaction(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='paystack_transactions')
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    amount_kobo = models.PositiveBigIntegerField(help_text='Amount in kobo (NGN x 100)')
    paystack_status = models.CharField(max_length=20, choices=PAYSTACK_STATUS, default='initiated')
    authorisation_url = models.URLField(blank=True)
    paystack_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments_paystack_transaction'
        ordering = ['-created_at']

    def __str__(self):
        return f"Txn {self.reference} [{self.paystack_status}]"


class RefundRequest(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='refund_requests')
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, related_name='refund_requests')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=REFUND_STATUS, default='pending')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments_refund_request'
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund for Order #{self.order_id} [{self.status}]"
