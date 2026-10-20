"""Management command: expire stale offers. Schedule every 15 minutes."""
from django.core.management.base import BaseCommand
from apps.negotiations.services import expire_stale_offers


class Command(BaseCommand):
    help = 'Expire pending offers that have passed their 48-hour window'

    def handle(self, *args, **options):
        count = expire_stale_offers()
        self.stdout.write(self.style.SUCCESS(f'Expired {count} stale offer(s).'))
