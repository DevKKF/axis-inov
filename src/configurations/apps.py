from django.apps import AppConfig


class ConfigurationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'configurations'
    verbose_name: str = 'Paramétrage'

    def ready(self):
        import configurations.signals
    
