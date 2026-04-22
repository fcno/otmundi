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

class KillStatsScraperProvider(BaseProvider[ProviderOutput]):
    def normalize_raw(self, data: RawProviderInput) -> ProviderOutput:
        return {
            "snapshot_id": data["snapshot_id"],
            "captured_at": data["captured_at"],
            "world_id": data["world"]["id"],
            "world_name": data["world"]["name"],
            "data": data["data"],
        }