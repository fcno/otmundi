import json
from io import StringIO
from pathlib import Path
from typing import Any

import pytest
from django.conf import settings
from django.core.management.base import OutputWrapper
from django.utils.translation import gettext_lazy as _

from apps.core.management.base_batch import BaseBatchIngestCommand


class MockBatchCommand(BaseBatchIngestCommand):
    feature_name = "test_feat"

    def process_data(self, data: dict[str, Any], filename: str) -> str:
        if "force_error" in data:
            raise ValueError("Erro simulado")
        return _("Processed {id}").format(id=data["id"])


@pytest.mark.django_db
class TestBaseBatchIngestCommand:
    @pytest.fixture(autouse=True)
    def setup_dirs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        self.base_dir = tmp_path / "data" / "test_feat"
        (self.base_dir / "pending").mkdir(parents=True)
        (self.base_dir / "imported").mkdir()
        (self.base_dir / "error").mkdir()

        monkeypatch.setattr(settings, "BASE_DIR", tmp_path)
        # Mocking get_commands para registrar o comando dummy se necessário
        # Ou instanciar diretamente para testar o handle

    def test_full_batch_lifecycle(self) -> None:
        """Testa um arquivo válido sendo movido para 'imported' e um inválido para 'error'."""
        pending = self.base_dir / "pending"

        # Arquivo 1: Sucesso
        (pending / "ok.json").write_text(json.dumps({"id": 1}))
        # Arquivo 2: Erro
        (pending / "fail.json").write_text(json.dumps({"force_error": True}))

        cmd = MockBatchCommand()
        stdout_buffer, stderr_buffer = StringIO(), StringIO()

        cmd.stdout = OutputWrapper(stdout_buffer)
        cmd.stderr = OutputWrapper(stderr_buffer)

        cmd.handle()

        # Validações de movimentação
        assert not (pending / "ok.json").exists()
        assert (self.base_dir / "imported" / "ok.json").exists()

        assert not (pending / "fail.json").exists()
        assert (self.base_dir / "error" / "fail.json").exists()

        # Validações de Log
        assert (
            _("Successfully processed ok.json").format(detail="Processed 1")
            in stdout_buffer.getvalue()
        )
        assert "Erro simulado" in stderr_buffer.getvalue()

    def test_no_files_found(self) -> None:
        """Garante que o comando encerra graciosamente sem arquivos."""
        cmd = MockBatchCommand()
        stdout_buffer = StringIO()
        cmd.stdout = OutputWrapper(stdout_buffer)

        cmd.handle()
        assert _("No files found.").format() in stdout_buffer.getvalue()
