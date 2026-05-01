from datetime import datetime

from apps.engine.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.game_data.monsters.models.monster import Monster
from apps.game_data.worlds.models.world import World


class MonsterEventService:
    @staticmethod
    def create_manual_puff(
        monster: Monster, timestamp: datetime, reported_by_id: int, world: World
    ) -> MonsterSpawnEvent:
        """
        Caminho WEB: Cria um evento marcado como Puff.
        Regra: Via Web é sempre Puff.
        """

        return MonsterSpawnEvent.objects.create(
            monster=monster,
            timestamp=timestamp,
            world=world,
            is_puff=True,  # Definido pela origem WEB
            reported_by_id=reported_by_id,
        )
