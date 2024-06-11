from django.core.management.base import BaseCommand
from huey.contrib.djhuey import HUEY


class Command(BaseCommand):
    help = 'Clears all tasks from the Huey queue'

    def handle(self, *args, **options):
        HUEY.flush()
        self.stdout.write(self.style.SUCCESS('Successfully cleared the Huey queue'))
