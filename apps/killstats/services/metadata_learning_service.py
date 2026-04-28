from django.db.models import F, Window
from django.db.models.functions import Lag

from apps.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.monsters.models.monster import Monster
from apps.monsters.models.monster_metadata import MonsterMetadata


class MetadataLearningService:
    @classmethod
    def recalibrate_monster(cls, monster: Monster) -> None:
        """Analisa o histórico completo e recalibra a janela global."""
        # 1. Calcula os deltas entre eventos consecutivos no mesmo mundo
        # Usamos Window Function para performance máxima no DB
        annotated_events = MonsterSpawnEvent.objects.filter(monster=monster).annotate(
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
            cls._apply_metadata(monster, min(intervals), max(intervals))

    @staticmethod
    def _apply_metadata(monster: Monster, observed_min: int, observed_max: int) -> None:
        """Aplica os novos limites ao Metadata global."""
        metadata, _ = MonsterMetadata.objects.get_or_create(monster=monster)

        updated = False

        # Se o observado for menor que o registrado (ou se estiver nulo)
        if metadata.min_interval is None or observed_min < metadata.min_interval:
            metadata.min_interval = observed_min
            updated = True

        # Se o observado for maior que o registrado (ou se estiver nulo)
        if metadata.max_interval is None or observed_max > metadata.max_interval:
            metadata.max_interval = observed_max
            updated = True

        if updated:
            metadata.save()

    @classmethod
    def full_recalibration(cls) -> None:
        """Recalibra todos os monstros usando iterator para segurança de memória."""
        # O .iterator() evita carregar todos os monstros na RAM de uma vez
        for monster in Monster.objects.all().iterator(chunk_size=100):
            cls.recalibrate_monster(monster)
