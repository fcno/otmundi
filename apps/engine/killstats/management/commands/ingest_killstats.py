# apps/engine/ingestion/management/commands/ingest_killstats.py
from typing import Any

from django.utils.translation import gettext as _

from apps.core.management.base_batch import BaseBatchIngestCommand
from apps.engine.killstats.ingestion.providers.killstats_scraper import (
    KillStatsScraperProvider,
)
from apps.engine.killstats.ingestion.repositories.killstats_repository import (
    KillStatsRepository,
)
from apps.engine.killstats.ingestion.services.ingest_killstats import (
    KillStatsIngestService,
)


class Command(BaseBatchIngestCommand):
    help = _("Batch ingest KillStats files from data/killstats/pending/")

    # Define a pasta como 'data/killstats/'
    feature_name = "killstats"

    def process_data(self, data: dict[str, Any], filename: str) -> str:
        """Implementação específica para KillStats."""
        service = KillStatsIngestService(
            provider=KillStatsScraperProvider(), repository=KillStatsRepository()
        )

        # O repositório agora aceita o nome do arquivo para log interno
        snapshot = service.ingest(data, source_file=filename)

        return _("Snapshot {id} created for {world}").format(
            id=snapshot.snapshot_id, world=snapshot.world.name
        )
