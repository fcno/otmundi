from django.apps import AppConfig


class KillstatsConfig(AppConfig):
    name = "apps.engine.killstats"
    label = "killstats"

    def ready(self) -> None:
        import apps.engine.killstats.signals  # noqa: F401
