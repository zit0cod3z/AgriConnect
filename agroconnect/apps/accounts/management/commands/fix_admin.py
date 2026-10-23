"""
Emergency: delete and recreate superuser cleanly.
Run with: python manage.py fix_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Delete and recreate the superuser cleanly'

    def handle(self, *args, **options):
        Customer = get_user_model()

        email = 'admin@agroconnect.ng'
        password = 'Admin@2026'

        # Delete any existing user with that email or username
        deleted, _ = Customer.objects.filter(email=email).delete()
        self.stdout.write(f'Deleted {deleted} existing user(s) with email {email}')

        # Create fresh superuser
        u = Customer.objects.create_superuser(
            username=email,
            email=email,
            password=password,
            first_name='Admin',
            last_name='AgroConnect',
            phone='',
            state='',
            email_verified=True,
        )

        # Verify it works
        from django.contrib.auth import authenticate
        result = authenticate(None, username=email, password=password)

        self.stdout.write(self.style.SUCCESS(
            f'Superuser created: {u.email}'
        ))
        self.stdout.write(f'  username     = {u.username}')
        self.stdout.write(f'  is_staff     = {u.is_staff}')
        self.stdout.write(f'  is_superuser = {u.is_superuser}')
        self.stdout.write(f'  is_active    = {u.is_active}')
        self.stdout.write(f'  authenticate = {"OK ✅" if result else "FAILED ❌"}')
        self.stdout.write(self.style.SUCCESS(
            f'\nLogin at /admin/ with:\n  Username: {email}\n  Password: {password}'
        ))
