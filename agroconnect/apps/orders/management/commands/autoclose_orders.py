"""Management command: auto-close stale delivered orders. Schedule daily."""
from django.core.management.base import BaseCommand
from apps.orders.services import auto_close_stale_orders


class Command(BaseCommand):
    help = 'Close orders stuck at delivered status for more than 7 days'

    def handle(self, *args, **options):
        count = auto_close_stale_orders()
        self.stdout.write(self.style.SUCCESS(f'Closed {count} stale order(s).'))
