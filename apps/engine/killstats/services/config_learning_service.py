from django.db.models import F, Window
from django.db.models.functions import Lag

from apps.engine.killstats.models.creature_config import CreatureConfig
from apps.engine.killstats.models.creature_spawn_event import CreatureSpawnEvent
from apps.game_data.creatures.models import Creature


class ConfigLearningService:
    @classmethod
    def recalibrate_creature(cls, creature: Creature) -> None:
        """Analisa o histórico completo e recalibra a janela global."""
        # 1. Calcula os deltas entre eventos consecutivos no mesmo mundo
        # Usamos Window Function para performance máxima no DB
        annotated_events = CreatureSpawnEvent.objects.filter(
            creature=creature
        ).annotate(
            prev_timestamp=Window(
                expression=Lag("timestamp"),
                partition_by=[F("world")],
                order_by=F("timestamp").asc(),
            )
        )

        # 2. Extrai os intervalos em dias
        intervals: list[int] = []
        for event in annotated_events:
            if event.prev_timestamp:
                delta_days = (event.timestamp - event.prev_timestamp).days
                # Filtro de sanidade: ignora spawns no mesmo dia (outliers)
                if delta_days >= 1:
                    intervals.append(delta_days)

        if intervals:
            cls._apply_config(creature, min(intervals), max(intervals))

    @staticmethod
    def _apply_config(creature: Creature, observed_min: int, observed_max: int) -> None:
        """Aplica os novos limites ao Config global."""
        config, _ = CreatureConfig.objects.get_or_create(creature=creature)

        updated = False

        # Se o observado for menor que o registrado (ou se estiver nulo)
        if config.min_interval is None or observed_min < config.min_interval:
            config.min_interval = observed_min
            updated = True

        # Se o observado for maior que o registrado (ou se estiver nulo)
        if config.max_interval is None or observed_max > config.max_interval:
            config.max_interval = observed_max
            updated = True

        if updated:
            config.save()

    @classmethod
    def full_recalibration(cls) -> None:
        """Recalibra todas as criaturas usando iterator para segurança de memória."""
        # O .iterator() evita carregar todas os criaturas na RAM de uma vez
        for creature in Creature.objects.all().iterator(chunk_size=100):
            cls.recalibrate_creature(creature)
