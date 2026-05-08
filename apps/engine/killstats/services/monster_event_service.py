from datetime import datetime
from typing import Any

from django.db.models import QuerySet

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

    @staticmethod
    def _calculate_intervals(events_by_world: dict[int, list[datetime]]) -> list[int]:
        """
        Lógica pura: extrai os intervalos em dias entre eventos por mundo.
        """
        intervals: list[int] = []
        for timestamps in events_by_world.values():
            if len(timestamps) < 2:
                continue

            sorted_ts = sorted(timestamps)
            for i in range(len(sorted_ts) - 1):
                diff = (sorted_ts[i + 1] - sorted_ts[i]).days
                if diff > 0:
                    intervals.append(diff)
        return intervals

    @classmethod
    def get_suggested_window(cls, monster_id: int) -> dict[str, Any]:
        """
        Orquestra a obtenção de dados e o cálculo da janela sugerida.
        """
        events: QuerySet[Any] = (
            MonsterSpawnEvent.objects.filter(monster_id=monster_id)
            .values("world_id", "timestamp")
            .order_by("world_id", "timestamp")
        )

        world_events: dict[int, list[datetime]] = {}
        for ev in events:
            world_events.setdefault(ev["world_id"], []).append(ev["timestamp"])

        intervals = cls._calculate_intervals(world_events)

        if not intervals:
            return {"suggested_min": None, "suggested_max": None, "sample_size": 0}

        return {
            "suggested_min": min(intervals),
            "suggested_max": max(intervals),
            "sample_size": len(intervals),
        }
