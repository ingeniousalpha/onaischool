from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    name = 'apps.integrations'

    def ready(self):
        super().ready()
