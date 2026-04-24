from typing import TypedDict

from .base import BaseProvider

# ===== RAW INPUT (externo) =====


class RawKillMetricDict(TypedDict):
    players_killed: int | str
    monsters_killed: int | str


class RawMonsterDict(TypedDict):
    monster: str
    last_day: RawKillMetricDict
    last_7_days: RawKillMetricDict


class RawWorldDict(TypedDict):
    id: str
    name: str


class RawProviderInput(TypedDict):
    snapshot_id: str
    captured_at: str
    world: RawWorldDict
    data: list[RawMonsterDict]


# ===== PROVIDER OUTPUT (ainda não normalizado) =====


class KillMetricDict(TypedDict):
    players_killed: int | str
    monsters_killed: int | str


class MonsterDict(TypedDict):
    monster: str
    last_day: KillMetricDict
    last_7_days: KillMetricDict


class ProviderOutput(TypedDict):
    snapshot_id: str
    captured_at: str
    world_id: str
    world_name: str
    data: list[MonsterDict]


# ===== PROVIDER =====


class KillStatsScraperProvider(BaseProvider[RawProviderInput, ProviderOutput]):
    def normalize_raw(self, data: RawProviderInput) -> ProviderOutput:
        # Usamos .get() com fallback None para que os validadores 'validate_required'
        # possam capturar a ausência do dado e lançar ValidationError corretamente.
        world = data.get("world", {})

        return {
            "snapshot_id": data.get("snapshot_id"),
            "captured_at": data.get("captured_at"),
            "world_id": world.get("id"),
            "world_name": world.get("name"),
            "data": data.get("data", []),
        }
