"""Management command: backup SQLite database. Schedule daily."""
import os
import shutil
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Backup the SQLite database and prune backups older than 30 days'

    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']
        backup_dir = settings.DB_BACKUP_DIR
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'db_{timestamp}.sqlite3'
        backup_path = os.path.join(backup_dir, backup_name)
        shutil.copy2(str(db_path), backup_path)
        self.stdout.write(self.style.SUCCESS(f'Database backed up to {backup_path}'))

        # Prune backups older than 30 days
        cutoff = datetime.now() - timedelta(days=30)
        pruned = 0
        for fname in os.listdir(backup_dir):
            if fname.startswith('db_') and fname.endswith('.sqlite3'):
                fpath = os.path.join(backup_dir, fname)
                mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                if mtime < cutoff:
                    os.remove(fpath)
                    pruned += 1
        if pruned:
            self.stdout.write(self.style.WARNING(f'Pruned {pruned} old backup(s).'))
