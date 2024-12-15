from django.core.management.base import BaseCommand, CommandError
from django.core import management

class Command(BaseCommand):
    def handle(self, *args, **options):
        management.call_command('flush',interactive=False)

        print("Unseeded")
