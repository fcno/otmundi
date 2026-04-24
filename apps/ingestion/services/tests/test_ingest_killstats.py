from typing import Any

import pytest

from apps.core.validators.base import ValidationError
from apps.ingestion.providers.killstats_scraper import KillStatsScraperProvider
from apps.ingestion.repositories.killstats_repository import KillStatsRepository
from apps.ingestion.services.ingest_killstats import KillStatsIngestService
from apps.killstats.models.killstat import KillStat


def build_valid_payload() -> dict[str, Any]:
    """Factory com dados originais para manter o histórico do Git limpo."""
    return {
        "snapshot_id": "test_snapshot_001",
        "captured_at": "2026-04-24T10:00:00Z",
        "world": {"id": "11", "name": "Auroria"},
        "data": [
            {
                "monster": "Dragon Lord",
                "last_day": {"players_killed": 10, "monsters_killed": 200},
                "last_7_days": {"players_killed": 50, "monsters_killed": 1000},
            }
        ],
    }


@pytest.fixture
def service() -> KillStatsIngestService:
    return KillStatsIngestService(KillStatsScraperProvider(), KillStatsRepository())


@pytest.mark.django_db
class TestKillStatsIngestService:

    def test_ingest_persists_every_single_field(
        self, service: KillStatsIngestService
    ) -> None:
        """Garante a persistência integral de todos os campos do payload."""
        payload = build_valid_payload()
        snapshot = service.ingest(payload)

        assert snapshot.snapshot_id == "test_snapshot_001"
        assert snapshot.world.name == "auroria"

        # Mypy: Type guard para evitar [union-attr]
        kill_stat: KillStat | None = snapshot.kill_stats.first()
        assert kill_stat is not None

        assert kill_stat.monster.name == "dragon lord"
        assert kill_stat.last_day_players_killed == 10
        assert kill_stat.last_day_monsters_killed == 200
        assert kill_stat.last_7_days_players_killed == 50
        assert kill_stat.last_7_days_monsters_killed == 1000

    def test_ingest_normalization_and_trim(
        self, service: KillStatsIngestService
    ) -> None:
        """Valida se o trim e lower funcionam em múltiplos níveis."""
        payload = build_valid_payload()
        payload["world"]["name"] = "   AURORIA   "
        payload["data"][0]["monster"] = "   DRAGON LORD   "

        snapshot = service.ingest(payload)

        kill_stat = snapshot.kill_stats.first()
        assert kill_stat is not None
        assert snapshot.world.name == "auroria"
        assert kill_stat.monster.name == "dragon lord"

    @pytest.mark.parametrize(
        "path, invalid_value",
        [
            (["snapshot_id"], None),
            (["world", "id"], None),
            (["captured_at"], "data-invalida"),
            (["data", 0, "monster"], ""),
        ],
    )
    def test_ingest_validation_integrity(
        self, service: KillStatsIngestService, path: list[Any], invalid_value: Any
    ) -> None:
        """Garante que falhas de contrato lancem a ValidationError customizada do Core."""
        payload = build_valid_payload()

        target = payload
        for step in path[:-1]:
            target = target[step]
        target[path[-1]] = invalid_value

        with pytest.raises(ValidationError):
            service.ingest(payload)

    def test_duplicate_snapshot_prevention(
        self, service: KillStatsIngestService
    ) -> None:
        """Valida a restrição de unicidade do banco de dados via Service."""
        payload = build_valid_payload()
        service.ingest(payload)

        # O segundo envio do mesmo payload deve disparar ValidationError (Unique)
        with pytest.raises(ValidationError):
            service.ingest(payload)
