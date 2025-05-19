from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ElectricAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.electric_app'

    def ready(self):
        import src.electric_app.signal_receivers # noqa
