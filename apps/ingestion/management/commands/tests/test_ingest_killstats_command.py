import json
from io import StringIO
from pathlib import Path

import pytest
from django.conf import settings
from django.core.management import CommandError, call_command

from apps.snapshots.models.snapshot import Snapshot


@pytest.mark.django_db
class TestIngestKillStatsCommand:
    @pytest.fixture(autouse=True)
    def setup_data_dirs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Configura a estrutura de diretórios e o BASE_DIR para o teste.
        O uso de pytest.MonkeyPatch garante a conformidade com o Mypy.
        """
        data_dir = tmp_path / "data"
        (data_dir / "pending").mkdir(parents=True)
        (data_dir / "imported").mkdir()
        (data_dir / "error").mkdir()

        # Redireciona o BASE_DIR do Django para o diretório temporário de testes
        monkeypatch.setattr(settings, "BASE_DIR", tmp_path)

    def test_command_flow_from_pending_to_imported_on_success(self) -> None:
        """
        Valida o ciclo de vida completo do ficheiro e persistência.
        Verifica o estado antes e depois da execução de forma agnóstica.
        """
        # 1. Preparação
        filename = "valid_killstats.json"
        snapshot_id = "success_state_999"
        world_name = "Antica"
        pending_dir = settings.BASE_DIR / "data" / "pending"
        imported_dir = settings.BASE_DIR / "data" / "imported"

        pending_file = pending_dir / filename
        data = {
            "snapshot_id": snapshot_id,
            "captured_at": "2026-04-24T10:00:00Z",
            "world": {"id": "1", "name": world_name},
            "data": [],
        }
        pending_file.write_text(json.dumps(data))

        # 2. Verificação de Estado Inicial (Pre-conditions)
        assert pending_file.exists()
        assert not (imported_dir / filename).exists()
        assert not Snapshot.objects.filter(snapshot_id=snapshot_id).exists()

        # 3. Execução
        out = StringIO()
        call_command("ingest_killstats", filename, stdout=out)

        # 4. Verificação de Estado Final (Post-conditions)
        assert not pending_file.exists()
        assert (imported_dir / filename).exists()

        # O registo deve existir no banco de dados
        assert Snapshot.objects.filter(snapshot_id=snapshot_id).exists()

        # Verificação de saída agnóstica a Locale e Case-sensitivity
        output = out.getvalue().lower()
        assert snapshot_id.lower() in output
        assert world_name.lower() in output

    def test_command_flow_from_pending_to_error_on_validation_failure(self) -> None:
        """
        Valida que ficheiros inválidos são movidos para a pasta de erro.
        Garante que a falha de validação não interrompe o sistema.
        """
        # 1. Preparação
        filename = "invalid_data.json"
        pending_dir = settings.BASE_DIR / "data" / "pending"
        error_dir = settings.BASE_DIR / "data" / "error"

        pending_file = pending_dir / filename
        # Payload sem 'snapshot_id' para forçar falha no pipeline de validação
        invalid_data = {
            "captured_at": "2026-04-24T10:00:00Z",
            "world": {"name": "Antica"},
        }
        pending_file.write_text(json.dumps(invalid_data))

        # 2. Verificação de Estado Inicial
        assert pending_file.exists()
        assert not (error_dir / filename).exists()

        # 3. Execução
        err = StringIO()
        call_command("ingest_killstats", filename, stderr=err)

        # 4. Verificação de Estado Final
        assert not pending_file.exists()
        assert (error_dir / filename).exists()

        # O erro deve indicar o campo técnico, independente da tradução
        assert "snapshot_id" in err.getvalue().lower()

    def test_command_file_not_found_raises_error(self) -> None:
        """Garante que o comando lança CommandError se o ficheiro não existir."""
        with pytest.raises(CommandError):
            call_command("ingest_killstats", "missing.json")
