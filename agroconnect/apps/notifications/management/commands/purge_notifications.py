"""Management command: purge old read notifications. Schedule daily."""
from django.core.management.base import BaseCommand
from apps.notifications.services import purge_old_notifications


class Command(BaseCommand):
    help = 'Delete read notifications older than 90 days'

    def handle(self, *args, **options):
        count = purge_old_notifications()
        self.stdout.write(self.style.SUCCESS(f'Purged {count} old notification(s).'))
