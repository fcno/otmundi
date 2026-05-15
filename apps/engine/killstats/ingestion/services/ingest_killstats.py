# apps/ingestion/services/ingest_killstats.py
from typing import Any, cast

from apps.core.helpers.sanitizers import sanitize_data
from apps.core.helpers.validate_and_normalize import validate_and_normalize
from apps.core.normalizers.datetime import normalize_datetime
from apps.core.normalizers.integers import normalize_integer
from apps.core.normalizers.strings import normalize_string
from apps.core.validators.datetime import validate_datetime
from apps.core.validators.integers import validate_integer
from apps.core.validators.required import validate_required
from apps.core.validators.strings import validate_string
from apps.core.validators.unique import validate_unique
from apps.engine.killstats.ingestion.dto import (
    CreatureStatsDTO,
    KillStatsMetricDTO,
    WorldKillStatsDTO,
)
from apps.engine.killstats.ingestion.providers.killstats_scraper import (
    KillStatsScraperProvider,
    ProviderOutput,
    RawProviderInput,
)
from apps.engine.killstats.ingestion.repositories.killstats_repository import (
    KillStatsRepository,
)
from apps.engine.snapshots.models.snapshot import Snapshot


class KillStatsIngestService:
    def __init__(
        self, provider: KillStatsScraperProvider, repository: KillStatsRepository
    ) -> None:
        self.provider = provider
        self.repository = repository

    def ingest(self, raw: dict[str, Any], source_file: str = "") -> Snapshot:
        """
        Processa os dados brutos, valida via DTO e persiste através do repositório.
        """
        sanitized = sanitize_data(raw)
        raw_input = cast(RawProviderInput, sanitized)
        data: ProviderOutput = self.provider.normalize_raw(raw_input)

        snapshot_id = validate_and_normalize(
            data["snapshot_id"],
            [
                validate_required(field="snapshot_id"),
                validate_string(field="snapshot_id"),
                validate_unique(model_class=Snapshot, field="snapshot_id"),
            ],
            normalize_string,
        )

        world_id = validate_and_normalize(
            data["world_id"],
            [validate_required(field="world_id"), validate_string(field="world_id")],
            normalize_string,
        )

        world_name = validate_and_normalize(
            data["world_name"],
            [
                validate_required(field="world_name"),
                validate_string(field="world_name"),
            ],
            normalize_string,
        )

        captured_at = validate_and_normalize(
            data["captured_at"],
            [
                validate_required(field="captured_at"),
                validate_datetime(field="captured_at"),
            ],
            normalize_datetime,
        )

        creatures: list[CreatureStatsDTO] = []
        for item in data["data"]:
            creature = validate_and_normalize(
                item["creature"],
                [
                    validate_required(field="creature"),
                    validate_string(field="creature"),
                ],
                normalize_string,
            )

            last_day = item["last_day"]
            last_7_days = item["last_7_days"]

            creatures.append(
                CreatureStatsDTO(
                    creature=creature,
                    last_day=KillStatsMetricDTO(
                        players_killed=validate_and_normalize(
                            last_day["players_killed"],
                            [
                                validate_required(field="players_killed"),
                                validate_integer(field="players_killed"),
                            ],
                            normalize_integer,
                        ),
                        creatures_killed=validate_and_normalize(
                            last_day["creatures_killed"],
                            [
                                validate_required(field="creatures_killed"),
                                validate_integer(field="creatures_killed"),
                            ],
                            normalize_integer,
                        ),
                    ),
                    last_7_days=KillStatsMetricDTO(
                        players_killed=validate_and_normalize(
                            last_7_days["players_killed"],
                            [
                                validate_required(field="players_killed"),
                                validate_integer(field="players_killed"),
                            ],
                            normalize_integer,
                        ),
                        creatures_killed=validate_and_normalize(
                            last_7_days["creatures_killed"],
                            [
                                validate_required(field="creatures_killed"),
                                validate_integer(field="creatures_killed"),
                            ],
                            normalize_integer,
                        ),
                    ),
                )
            )

        dto = WorldKillStatsDTO(
            snapshot_id=snapshot_id,
            captured_at=captured_at,
            world_id=world_id,
            world_name=world_name,
            data=creatures,
        )

        # O Service entrega o DTO validado para o Repository salvar
        return self.repository.save_world_kill_stats(dto, source_file=source_file)
