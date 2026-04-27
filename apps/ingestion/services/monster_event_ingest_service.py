from datetime import datetime

from apps.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.monsters.models.monster import Monster
from apps.worlds.models.world import World


class MonsterEventIngestService:
    @staticmethod
    def create_event_from_ingestion(
        monster: Monster, timestamp: datetime, world: World
    ) -> MonsterSpawnEvent:
        """
        Gera um evento de Spawn baseado em um registro de KillStat.
        Regra: Ingestion JSON é sempre um abate real (is_puff=False).
        """
        return MonsterSpawnEvent(
            monster=monster,
            timestamp=timestamp,
            world=world,
            is_puff=False,  # Definido pela origem JSON
            reported_by=None,  # Ingestão automática não tem usuário
        )
