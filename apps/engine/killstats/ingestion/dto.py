from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class KillStatsMetricDTO:
    players_killed: int
    creatures_killed: int


@dataclass(frozen=True)
class CreatureStatsDTO:
    creature: str
    last_day: KillStatsMetricDTO
    last_7_days: KillStatsMetricDTO


@dataclass(frozen=True)
class WorldKillStatsDTO:
    snapshot_id: str
    captured_at: datetime
    world_id: str
    world_name: str
    data: list[CreatureStatsDTO]
