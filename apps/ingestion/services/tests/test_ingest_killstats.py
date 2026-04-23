from datetime import datetime
from typing import Any

import pytest

from apps.core.validators.base import ValidationError
from apps.ingestion.providers.killstats_scraper import KillStatsScraperProvider
from apps.ingestion.services.ingest_killstats import KillStatsIngestService
from apps.snapshots.models.snapshot import Snapshot
from apps.worlds.models.world import World


def build_valid_payload() -> dict[str, Any]:
    return {
        "snapshot_id": "2026-04-20T19:32:24+00:00_11",
        "captured_at": "2026-04-20T19:32:24+00:00",
        "world": {"id": "11", "name": "Auroria"},
        "data": [
            {
                "monster": "Dragon Lord",
                "last_day": {"players_killed": 0, "monsters_killed": 10},
                "last_7_days": {"players_killed": 1, "monsters_killed": 20},
            }
        ],
    }


# ===== SUCCESS & INTEGRATION =====


@pytest.mark.django_db
def test_ingest_full_pipeline() -> None:
    service = KillStatsIngestService(KillStatsScraperProvider())
    result = service.ingest(build_valid_payload())

    assert result.snapshot_id == "2026-04-20t19:32:24+00:00_11"
    assert isinstance(result.captured_at, datetime)
    assert result.world_id == "11"
    assert result.world_name == "auroria"

    m = result.data[0]
    assert m.monster == "dragon lord"
    assert m.last_day.players_killed == 0
    assert m.last_day.monsters_killed == 10
    assert m.last_7_days.players_killed == 1
    assert m.last_7_days.monsters_killed == 20


@pytest.mark.django_db
def test_ingest_sanitizes_dirty_input() -> None:
    """Garante que o serviço limpa espaços (trim) antes da normalização."""
    service = KillStatsIngestService(KillStatsScraperProvider())
    payload = build_valid_payload()

    # Input "sujo" com espaços extras
    payload["world"]["name"] = "   Auroria   "
    payload["data"][0]["monster"] = "   Dragon Lord   "

    result = service.ingest(payload)

    assert result.world_name == "auroria"
    assert result.data[0].monster == "dragon lord"


# ===== ROOT REQUIRED vs TYPE =====


def test_snapshot_id_required() -> None:
    payload = build_valid_payload()
    payload["snapshot_id"] = None

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


def test_snapshot_id_empty_string() -> None:
    """Com o sanitizer, '   ' vira None e falha no required."""
    payload = build_valid_payload()
    payload["snapshot_id"] = "   "

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


def test_snapshot_id_not_string() -> None:
    payload = build_valid_payload()
    payload["snapshot_id"] = 123

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


@pytest.mark.django_db
def test_captured_at_required() -> None:
    payload = build_valid_payload()
    payload["captured_at"] = None

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


@pytest.mark.django_db
def test_captured_at_invalid_format() -> None:
    payload = build_valid_payload()
    payload["captured_at"] = "invalid"

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


# ===== WORLD =====


@pytest.mark.django_db
def test_world_id_required() -> None:
    payload = build_valid_payload()
    payload["world"]["id"] = None

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


@pytest.mark.django_db
def test_world_name_empty() -> None:
    payload = build_valid_payload()
    payload["world"]["name"] = "   "

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


# ===== MONSTER =====


@pytest.mark.django_db
def test_monster_required() -> None:
    payload = build_valid_payload()
    payload["data"][0]["monster"] = None

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


@pytest.mark.django_db
def test_monster_empty() -> None:
    payload = build_valid_payload()
    payload["data"][0]["monster"] = "   "

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


@pytest.mark.django_db
def test_monster_not_string() -> None:
    payload = build_valid_payload()
    payload["data"][0]["monster"] = 123

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


# ===== METRICS (REQUIRED vs TYPE) =====


@pytest.mark.django_db
def test_players_killed_required() -> None:
    payload = build_valid_payload()
    payload["data"][0]["last_day"]["players_killed"] = None

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


@pytest.mark.django_db
def test_players_killed_invalid_type() -> None:
    payload = build_valid_payload()
    payload["data"][0]["last_day"]["players_killed"] = "abc"

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


@pytest.mark.django_db
def test_monsters_killed_required() -> None:
    payload = build_valid_payload()
    payload["data"][0]["last_day"]["monsters_killed"] = None

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


@pytest.mark.django_db
def test_monsters_killed_invalid_type() -> None:
    payload = build_valid_payload()
    payload["data"][0]["last_day"]["monsters_killed"] = "abc"

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


@pytest.mark.django_db
def test_last_day_players_invalid() -> None:
    payload = build_valid_payload()
    payload["data"][0]["last_day"]["players_killed"] = "abc"

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


@pytest.mark.django_db
def test_last_day_monsters_invalid() -> None:
    payload = build_valid_payload()
    payload["data"][0]["last_day"]["monsters_killed"] = "abc"

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


@pytest.mark.django_db
def test_last_7_days_players_invalid() -> None:
    payload = build_valid_payload()
    payload["data"][0]["last_7_days"]["players_killed"] = "abc"

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


@pytest.mark.django_db
def test_last_7_days_monsters_invalid() -> None:
    payload = build_valid_payload()
    payload["data"][0]["last_7_days"]["monsters_killed"] = "abc"

    with pytest.raises(ValidationError):
        KillStatsIngestService(KillStatsScraperProvider()).ingest(payload)


@pytest.mark.django_db
def test_ingest_fails_if_snapshot_id_already_exists() -> None:
    """Valida se o Fail-Fast de unicidade está funcionando no Service."""
    service = KillStatsIngestService(KillStatsScraperProvider())
    payload = build_valid_payload()
    snapshot_id = payload["snapshot_id"]

    # Simulamos que o snapshot já existe criando um no banco
    world = World.objects.create(name="auroria", external_id="11")
    Snapshot.objects.create(
        snapshot_id=snapshot_id,
        world=world,
        captured_at="2026-04-20T19:32:24Z",
        source_file="old.json",
    )

    # A tentativa de ingerir o mesmo snapshot_id deve levantar ValidationError
    with pytest.raises(ValidationError) as exc:
        service.ingest(payload)

    assert "already exists" in str(exc.value)
