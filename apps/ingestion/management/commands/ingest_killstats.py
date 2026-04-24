import json
import shutil
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from apps.core.validators.base import ValidationError
from apps.ingestion.providers.killstats_scraper import KillStatsScraperProvider
from apps.ingestion.repositories.killstats_repository import KillStatsRepository
from apps.ingestion.services.ingest_killstats import KillStatsIngestService


class Command(BaseCommand):
    help = _("Perform ingestion of KillStats data from a JSON file.")

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "filename",
            type=str,
            help=_("Name of the file inside data/pending/ to be processed."),
        )

    def handle(self, *args: Any, **options: Any) -> None:
        filename: str = options["filename"]

        # Caminhos baseados na pasta 'data' na raiz do projeto
        base_data_path = settings.BASE_DIR / "data"
        pending_path = base_data_path / "pending" / filename
        imported_dir = base_data_path / "imported"
        error_dir = base_data_path / "error"

        if not pending_path.exists():
            raise CommandError(
                _("File not found in pending folder: {path}").format(path=pending_path)
            )

        try:
            with pending_path.open("r", encoding="utf-8") as f:
                raw_data: dict[str, Any] = json.load(f)
        except json.JSONDecodeError as e:
            self._move_file(pending_path, error_dir)
            raise CommandError(_("JSON decoding error: {error}").format(error=e))

        service = KillStatsIngestService(
            provider=KillStatsScraperProvider(), repository=KillStatsRepository()
        )

        try:
            self.stdout.write(
                self.style.HTTP_INFO(
                    _("Starting ingestion: {name}").format(name=filename)
                )
            )

            snapshot = service.ingest(raw_data)

            self._move_file(pending_path, imported_dir)

            success_msg = _("Success! Snapshot '{id}' created for world '{world}'.")
            self.stdout.write(
                self.style.SUCCESS(
                    success_msg.format(
                        id=snapshot.snapshot_id, world=snapshot.world.name
                    )
                )
            )
        except ValidationError as e:
            self._move_file(pending_path, error_dir)
            self.stderr.write(
                self.style.ERROR(_("Validation Error: {error}").format(error=e))
            )
        except Exception as e:
            self._move_file(pending_path, error_dir)
            self.stderr.write(
                self.style.ERROR(
                    _("Unexpected error during ingestion: {error}").format(error=e)
                )
            )

    def _move_file(self, source_path: Path, destination_dir: Path) -> None:
        """Move o arquivo para o diretório de destino, garantindo que a pasta exista."""
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination_path = destination_dir / source_path.name

        # Se o arquivo já existir no destino (ex: re-processamento), removemos antes de mover
        if destination_path.exists():
            destination_path.unlink()

        shutil.move(str(source_path), str(destination_path))
