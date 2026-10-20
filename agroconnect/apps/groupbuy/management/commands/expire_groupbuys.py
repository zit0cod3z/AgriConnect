"""Management command: expire stale group buys. Schedule every hour."""
from django.core.management.base import BaseCommand
from apps.groupbuy.services import expire_stale_groupbuys


class Command(BaseCommand):
    help = 'Expire group buys that passed their 7-day window without reaching threshold'

    def handle(self, *args, **options):
        count = expire_stale_groupbuys()
        self.stdout.write(self.style.SUCCESS(f'Expired {count} group buy(s).'))
