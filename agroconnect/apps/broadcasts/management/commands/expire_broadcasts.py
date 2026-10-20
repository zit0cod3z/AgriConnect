"""Management command: expire stale broadcasts. Schedule every 5 minutes."""
from django.core.management.base import BaseCommand
from apps.broadcasts.services import expire_stale_broadcasts


class Command(BaseCommand):
    help = 'Expire price broadcasts past their expiry date'

    def handle(self, *args, **options):
        count = expire_stale_broadcasts()
        self.stdout.write(self.style.SUCCESS(f'Expired {count} broadcast(s).'))
