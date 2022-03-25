from django.apps import AppConfig
import ray

NumCPUs = 4


class StartupFundingsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'startup_fundings_app'

    def ready(self):
        ray.init(num_cpus=NumCPUs)
