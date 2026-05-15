from datetime import datetime

from apps.engine.killstats.models.creature_spawn_event import CreatureSpawnEvent
from apps.game_data.creatures.models.creature import Creature
from apps.game_data.worlds.models.world import World


class CreatureEventIngestService:
    @staticmethod
    def create_event_from_ingestion(
        creature: Creature, timestamp: datetime, world: World
    ) -> CreatureSpawnEvent:
        """
        Gera um evento de Spawn baseado em um registro de KillStat.
        Regra: Ingestion JSON é sempre um abate real (is_puff=False).
        """
        return CreatureSpawnEvent(
            creature=creature,
            timestamp=timestamp,
            world=world,
            is_puff=False,  # Definido pela origem JSON
            reported_by=None,  # Ingestão automática não tem usuário
        )
