# apps/core/management/base_batch.py
import json
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _


class BaseBatchIngestCommand(BaseCommand, ABC):
    """
    Classe base para comandos de ingestão em lote (Batch).
    Varre um diretório específico, processa arquivo por arquivo e move conforme o resultado.
    """

    @property
    @abstractmethod
    def feature_name(self) -> str:
        """Nome do módulo (ex: 'killstats') para definir a estrutura de pastas."""
        pass

    @abstractmethod
    def process_data(self, data: dict[str, Any], filename: str) -> str:
        """
        Lógica específica de processamento.
        Deve retornar uma string de sucesso para o log.
        """
        pass

    def handle(self, *args: Any, **options: Any) -> None:
        paths = self._setup_directories()
        files = sorted(paths["pending"].glob("*.json"))

        if not files:
            self.stdout.write(self.style.WARNING(_("No files found.")))
            return

        for file_path in files:
            self._execute_file_processing(file_path, paths)

    def _setup_directories(self) -> dict[str, Path]:
        """Cuida apenas da criação das pastas."""
        base = settings.BASE_DIR / "data" / self.feature_name
        dirs = {
            "pending": base / "pending",
            "imported": base / "imported",
            "error": base / "error",
        }
        for d in dirs.values():
            d.mkdir(parents=True, exist_ok=True)
        return dirs

    def _execute_file_processing(self, file_path: Path, paths: dict[str, Path]) -> None:
        """Cuida do ciclo de vida de um único arquivo."""
        filename = file_path.name
        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            detail = self.process_data(data, filename)

            self._move_file(file_path, paths["imported"])
            self.stdout.write(
                self.style.SUCCESS(
                    _("Successfully processed {file}: {detail}").format(
                        file=filename, detail=detail
                    )
                )
            )

        except Exception as e:
            self._move_file(file_path, paths["error"])
            self.stderr.write(
                self.style.ERROR(
                    _("Failed to process {file}: {error}").format(
                        file=filename, error=str(e)
                    )
                )
            )

    def _move_file(self, source_path: Path, destination_dir: Path) -> None:
        """Move o arquivo para o destino, sobrescrevendo se necessário."""
        destination_path = destination_dir / source_path.name
        if destination_path.exists():
            destination_path.unlink()
        shutil.move(str(source_path), str(destination_path))
