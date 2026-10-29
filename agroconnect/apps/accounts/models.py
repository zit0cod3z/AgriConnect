from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Customer(AbstractUser):
    """Extended user model for registered customers."""
    phone       = models.CharField(max_length=20, blank=True)
    state       = models.CharField(max_length=50, blank=True)
    address     = models.TextField(blank=True, help_text='Default delivery/home address')
    store_name  = models.CharField(max_length=200, blank=True, help_text='Farm/store name (farmers)')
    store_address = models.TextField(blank=True, help_text='Farm/store pickup address (farmers)')
    store_lat   = models.FloatField(null=True, blank=True)
    store_lng   = models.FloatField(null=True, blank=True)
    email_verified          = models.BooleanField(default=False)
    is_locked               = models.BooleanField(default=False)
    locked_until            = models.DateTimeField(null=True, blank=True)
    failed_login_attempts   = models.IntegerField(default=0)

    class Meta:
        db_table = 'accounts_customer'

    def __str__(self):
        return self.email or self.username

    @property
    def is_account_locked(self):
        if self.is_locked and self.locked_until:
            return timezone.now() < self.locked_until
        return False
