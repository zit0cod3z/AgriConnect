"""
Emergency: delete and recreate superuser cleanly.
Run with: python manage.py fix_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model, authenticate


class Command(BaseCommand):
    help = 'Delete and recreate the superuser cleanly'

    def handle(self, *args, **options):
        Customer = get_user_model()

        email = 'admin@agroconnect.ng'
        password = 'Admin@2026'

        # Delete any existing
        deleted, _ = Customer.objects.filter(email=email).delete()
        self.stdout.write(f'Deleted {deleted} existing user(s)')

        # Also delete by username in case there is a mismatch
        Customer.objects.filter(username=email).delete()

        # Create fresh
        u = Customer(
            username=email,
            email=email,
            first_name='Admin',
            last_name='AgroConnect',
            phone='',
            state='',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            email_verified=True,
        )
        u.set_password(password)
        u.save()

        # Reload from DB
        u.refresh_from_db()

        # Test authenticate
        result = authenticate(None, username=email, password=password)

        self.stdout.write(f'  pk           = {u.pk}')
        self.stdout.write(f'  username     = "{u.username}"')
        self.stdout.write(f'  email        = "{u.email}"')
        self.stdout.write(f'  is_staff     = {u.is_staff}')
        self.stdout.write(f'  is_superuser = {u.is_superuser}')
        self.stdout.write(f'  is_active    = {u.is_active}')
        self.stdout.write(f'  has_usable_password = {u.has_usable_password()}')
        self.stdout.write(f'  authenticate("{email}") = {"OK ✅" if result else "FAIL ❌"}')

        if result:
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Admin ready! Login at /admin/\n'
                f'   Username: {email}\n'
                f'   Password: {password}'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                '\n❌ authenticate() still failing — check AUTHENTICATION_BACKENDS in settings'
            ))
