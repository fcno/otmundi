from django.apps import AppConfig


class KillstatsConfig(AppConfig):
    name = "apps.killstats"

    def ready(self) -> None:
        import apps.killstats.signals  # noqa: F401
