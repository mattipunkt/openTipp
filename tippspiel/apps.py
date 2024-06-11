from django.apps import AppConfig
from django.apps import AppConfig
from huey.contrib.djhuey import periodic_task
from huey import crontab
from datetime import timedelta


class TippspielConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tippspiel'

    def ready(self):
        from .tasks import change_game
        # Registriere die Periodic Task beim Start
        from . import tasks
        tasks.change_game()
