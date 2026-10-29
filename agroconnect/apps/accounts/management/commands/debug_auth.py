"""
Debug auth on Render. Run: python manage.py debug_auth
Prints everything about the admin user and authentication.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password


class Command(BaseCommand):
    help = 'Debug admin authentication'

    def handle(self, *args, **options):
        Customer = get_user_model()
        email = 'admin@agroconnect.ng'
        password = 'Admin@2026'

        self.stdout.write(f'\nTotal users in DB: {Customer.objects.count()}')
        self.stdout.write(f'Staff users: {Customer.objects.filter(is_staff=True).count()}')
        self.stdout.write(f'Superusers: {Customer.objects.filter(is_superuser=True).count()}')

        user = Customer.objects.filter(email=email).first()
        if not user:
            self.stdout.write(self.style.ERROR(f'No user with email={email} found!'))
            self.stdout.write('All users:')
            for u in Customer.objects.all():
                self.stdout.write(f'  pk={u.pk} username="{u.username}" email="{u.email}" staff={u.is_staff}')
            return

        self.stdout.write(f'\nFound user:')
        self.stdout.write(f'  pk={user.pk}')
        self.stdout.write(f'  username="{user.username}"')
        self.stdout.write(f'  email="{user.email}"')
        self.stdout.write(f'  is_staff={user.is_staff}')
        self.stdout.write(f'  is_superuser={user.is_superuser}')
        self.stdout.write(f'  is_active={user.is_active}')
        self.stdout.write(f'  has_usable_password={user.has_usable_password()}')
        self.stdout.write(f'  check_password("{password}") = {check_password(password, user.password)}')

        # Try both username and email
        r1 = authenticate(None, username=user.username, password=password)
        r2 = authenticate(None, username=email, password=password)
        self.stdout.write(f'  authenticate(username="{user.username}") = {"OK" if r1 else "FAIL"}')
        self.stdout.write(f'  authenticate(username="{email}") = {"OK" if r2 else "FAIL"}')

        from django.conf import settings
        self.stdout.write(f'\nAUTHENTICATION_BACKENDS = {settings.AUTHENTICATION_BACKENDS}')
        self.stdout.write(f'AUTH_USER_MODEL = {settings.AUTH_USER_MODEL}')
