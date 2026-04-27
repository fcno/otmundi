from datetime import UTC, datetime

import pytest
from django.utils import timezone

from apps.ingestion.services.monster_event_ingest_service import (
    MonsterEventIngestService,
)
from apps.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.monsters.models.monster import Monster


@pytest.mark.django_db
class TestMonsterEventIngestService:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.service = MonsterEventIngestService()
        self.monster = Monster.objects.create(name="orshabaal")

    def test_create_event_from_ingestion_fields_integrity(self) -> None:
        """
        Garante que todos os campos da instância retornada estão
        corretos e tipados conforme a regra de ingestão.
        """
        now = datetime(2026, 4, 27, 14, 0, tzinfo=UTC)

        event = self.service.create_event_from_ingestion(self.monster, now)

        assert isinstance(event, MonsterSpawnEvent)
        assert event.monster == self.monster
        assert event.timestamp == now
        assert event.is_puff is False  # Regra de ouro: Ingestão nunca é puff
        assert event.reported_by is None  # Automação não possui usuário

    def test_create_event_does_not_persist_automatically(self) -> None:
        """
        Cenário de Borda: O serviço deve apenas instanciar o objeto.
        O salvamento deve ser responsabilidade do bulk_create no Repository.
        """
        now = timezone.now()

        event = self.service.create_event_from_ingestion(self.monster, now)

        assert event.pk is None  # O objeto não deve ter ID ainda (não salvo no banco)
        assert MonsterSpawnEvent.objects.count() == 0

    def test_create_event_with_different_monsters(self) -> None:
        """
        Garante que o serviço vincula o evento ao monstro correto
        mesmo se múltiplos forem processados.
        """
        ferumbras = Monster.objects.create(name="ferumbras")
        now = timezone.now()

        event_orsh = self.service.create_event_from_ingestion(self.monster, now)
        event_feru = self.service.create_event_from_ingestion(ferumbras, now)

        assert event_orsh.monster.name == "orshabaal"
        assert event_feru.monster.name == "ferumbras"

    def test_create_event_timestamp_precision(self) -> None:
        """
        Garante que o timestamp não sofre mutação ou truncamento
        indesejado durante a criação da instância.
        """
        complex_date = datetime(2026, 4, 27, 14, 5, 30, 123456, tzinfo=UTC)

        event = self.service.create_event_from_ingestion(self.monster, complex_date)

        assert event.timestamp == complex_date
