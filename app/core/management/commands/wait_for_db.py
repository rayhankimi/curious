"""
Django command to pause execution until database is available
"""

import time

from psycopg2 import OperationalError as Psycopg2OpError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for the database to be available"""
    def handle(self, *args, **options):
        """Entrypoint for commands"""
        self.stdout.write('Waiting for database...')
        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (OperationalError,Psycopg2OpError):
                self.stdout.write(self.style.ERROR('Database not available,'
                                                   'waiting for 1 second'))
                time.sleep(1)
            self.stdout.write(self.style.SUCCESS('Database available'))
