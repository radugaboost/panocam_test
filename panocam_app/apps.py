from django.apps import AppConfig


class PanocamAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'panocam_app'

    def ready(self):
        import panocam_app.signals

