# apps/ingestion/tests/test_dto.py
import dataclasses
from datetime import UTC, datetime

import pytest

from apps.ingestion.dto import (
    KillStatsMetricDTO,
    MonsterStatsDTO,
    WorldKillStatsDTO,
)


def test_killstats_metric_dto_all_fields() -> None:
    dto = KillStatsMetricDTO(players_killed=1, monsters_killed=2)

    assert dto.players_killed == 1
    assert dto.monsters_killed == 2


def test_monster_stats_dto_all_fields() -> None:
    last_day = KillStatsMetricDTO(1, 2)
    last_7_days = KillStatsMetricDTO(3, 4)

    dto = MonsterStatsDTO(
        monster="dragon",
        last_day=last_day,
        last_7_days=last_7_days,
    )

    assert dto.monster == "dragon"
    assert dto.last_day is last_day
    assert dto.last_7_days is last_7_days


def test_world_killstats_dto_all_fields() -> None:
    dt = datetime(2026, 1, 1, tzinfo=UTC)

    data = [
        MonsterStatsDTO(
            monster="dragon",
            last_day=KillStatsMetricDTO(1, 2),
            last_7_days=KillStatsMetricDTO(3, 4),
        )
    ]

    dto = WorldKillStatsDTO(
        snapshot_id="snap1",
        captured_at=dt,
        world_id="11",
        world_name="auroria",
        data=data,
    )

    assert dto.snapshot_id == "snap1"
    assert dto.captured_at == dt
    assert dto.captured_at.tzinfo is not None
    assert dto.world_id == "11"
    assert dto.world_name == "auroria"
    assert dto.data == data


def test_dto_is_immutable() -> None:
    dto = KillStatsMetricDTO(players_killed=1, monsters_killed=2)

    with pytest.raises(dataclasses.FrozenInstanceError):
        dto.players_killed = 10  # type: ignore[misc]
