"""
Auto-creates a Django superuser on deploy if one doesn't already exist.
Reads credentials from environment variables:
  DJANGO_SUPERUSER_EMAIL
  DJANGO_SUPERUSER_PASSWORD
Safe to run multiple times — idempotent.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create superuser from env vars if one does not already exist'

    def handle(self, *args, **options):
        Customer = get_user_model()

        email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', '').strip()
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '').strip()

        if not email or not password:
            self.stdout.write(self.style.WARNING(
                'Skipping superuser creation — '
                'DJANGO_SUPERUSER_EMAIL or DJANGO_SUPERUSER_PASSWORD not set.'
            ))
            return

        if Customer.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS(f'Superuser already exists: {email}'))
            return

        # username must equal email so Django admin ModelBackend can authenticate
        Customer.objects.create_superuser(
            username=email,
            email=email,
            password=password,
            phone='',
            state='',
            email_verified=True,
        )
        self.stdout.write(self.style.SUCCESS(f'Superuser created: {email}'))
