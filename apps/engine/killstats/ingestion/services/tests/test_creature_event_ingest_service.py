from datetime import UTC, datetime

import pytest
from django.utils import timezone

from apps.engine.killstats.ingestion.services.creature_event_ingest_service import (
    CreatureEventIngestService,
)
from apps.engine.killstats.models.creature_config import CreatureConfig
from apps.engine.killstats.models.creature_spawn_event import CreatureSpawnEvent
from apps.game_data.creatures.models.creature import Creature
from apps.game_data.worlds.models.world import World


@pytest.mark.django_db
class TestCreatureEventIngestService:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.service = CreatureEventIngestService()
        self.creature = Creature.objects.create(name="orshabaal")
        CreatureConfig.objects.create(creature=self.creature, is_active=True)
        self.world = World.objects.create(name="antica")

    def test_create_event_from_ingestion_fields_integrity(self) -> None:
        """
        Garante que todos os campos da instância retornada estão
        corretos e tipados conforme a regra de ingestão.
        """
        now = datetime(2026, 4, 27, 14, 0, tzinfo=UTC)

        event = self.service.create_event_from_ingestion(self.creature, now, self.world)

        assert isinstance(event, CreatureSpawnEvent)
        assert event.creature == self.creature
        assert event.world == self.world
        assert event.timestamp == now
        assert event.is_puff is False  # Regra de ouro: Ingestão nunca é puff
        assert event.reported_by is None  # Automação não possui usuário

    def test_create_event_does_not_persist_automatically(self) -> None:
        """
        Cenário de Borda: O serviço deve apenas instanciar o objeto.
        O salvamento deve ser responsabilidade do bulk_create no Repository.
        """
        now = timezone.now()

        event = self.service.create_event_from_ingestion(self.creature, now, self.world)

        assert event.pk is None  # O objeto não deve ter ID ainda (não salvo no banco)
        assert CreatureSpawnEvent.objects.count() == 0

    def test_create_event_with_different_creatures(self) -> None:
        """
        Garante que o serviço vincula o evento à criatura correta
        mesmo se múltiplas forem processadas.
        """
        ferumbras = Creature.objects.create(name="ferumbras")
        CreatureConfig.objects.create(creature=ferumbras, is_active=True)
        now = timezone.now()

        event_orsh = self.service.create_event_from_ingestion(
            self.creature, now, self.world
        )
        event_feru = self.service.create_event_from_ingestion(
            ferumbras, now, self.world
        )

        assert event_orsh.creature.name == "orshabaal"
        assert event_feru.creature.name == "ferumbras"

    def test_create_event_timestamp_precision(self) -> None:
        """
        Garante que o timestamp não sofre mutação ou truncamento
        indesejado durante a criação da instância.
        """
        complex_date = datetime(2026, 4, 27, 14, 5, 30, 123456, tzinfo=UTC)

        event = self.service.create_event_from_ingestion(
            self.creature, complex_date, self.world
        )

        assert event.timestamp == complex_date
