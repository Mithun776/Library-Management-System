from django.apps import AppConfig


class Cse_deptConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cse_dept'

    # to update import the signals module to register the signals
    def ready(self):
        from . import signals