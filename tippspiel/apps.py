from django.apps import AppConfig
from . import tasks


class TippspielConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tippspiel'

    def ready(self):
        tasks.change_game()
