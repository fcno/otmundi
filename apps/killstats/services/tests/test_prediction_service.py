from datetime import timedelta

import pytest
from django.utils import timezone

from apps.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.killstats.services.prediction_service import (
    PredictionService,
    PredictionStatus,
)
from apps.monsters.models.monster import Monster
from apps.monsters.models.monster_metadata import MonsterMetadata
from apps.worlds.models.world import World


@pytest.mark.django_db
class TestPredictionService:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.world = World.objects.create(name="Antica")
        self.monster = Monster.objects.create(name="Orshabaal")
        # Janela de 10 a 20 dias (Total de 11 dias possíveis)
        self.metadata = MonsterMetadata.objects.create(
            monster=self.monster, min_interval=10, max_interval=20
        )

    def _create_event(self, days_ago: int) -> None:
        """Helper para criar eventos no passado."""
        timestamp = timezone.now() - timedelta(days=days_ago)
        MonsterSpawnEvent.objects.create(
            monster=self.monster,
            world=self.world,
            timestamp=timestamp,
        )

    def test_status_collecting_data_no_event(self) -> None:
        """Caso o boss nunca tenha sido visto no mundo."""
        result = PredictionService.get_prediction(self.monster, self.world)
        assert result["status_code"] == PredictionStatus.COLLECTING.value
        assert result["chance_percentage"] == 0.0

    def test_status_no_chance(self) -> None:
        """Boss morreu há 5 dias, janela mínima é 10."""
        self._create_event(days_ago=5)
        result = PredictionService.get_prediction(self.monster, self.world)
        assert result["status_code"] == PredictionStatus.NO_CHANCE.value
        assert result["chance_percentage"] == 0.0

    def test_status_expected_soon_at_start_border_has_initial_chance(self) -> None:
        """No dia 10 (início), a chance deve ser > 0 (aprox 9.09%)."""
        self._create_event(days_ago=10)
        result = PredictionService.get_prediction(self.monster, self.world)
        assert result["status_code"] == PredictionStatus.EXPECTED.value
        assert result["chance_percentage"] == 9.09

    def test_status_expected_soon_mid_window(self) -> None:
        """Meio da janela: 15 dias."""
        self._create_event(days_ago=15)
        result = PredictionService.get_prediction(self.monster, self.world)
        assert result["status_code"] == PredictionStatus.EXPECTED.value
        assert result["chance_percentage"] == 54.55

    def test_status_expected_soon_at_end_border_is_100(self) -> None:
        """No dia 20 (fim da janela), a chance deve ser exatamente 100%."""
        self._create_event(days_ago=20)
        result = PredictionService.get_prediction(self.monster, self.world)
        assert result["status_code"] == PredictionStatus.EXPECTED.value
        assert result["chance_percentage"] == 100.0

    def test_status_overdue_remains_100(self) -> None:
        """Fora da janela (atrasado), mantém 100% para indicar urgência."""
        self._create_event(days_ago=21)
        result = PredictionService.get_prediction(self.monster, self.world)
        assert result["status_code"] == PredictionStatus.OVERDUE.value
        assert result["chance_percentage"] == 100.0

    def test_status_missing_probable_puff(self) -> None:
        """Extremo: Passou 20% do limite máximo."""
        self._create_event(days_ago=25)
        result = PredictionService.get_prediction(self.monster, self.world)
        assert result["status_code"] == PredictionStatus.MISSING.value
        assert result["chance_percentage"] == 0

    def test_metadata_null_intervals(self) -> None:
        """Garante que se os campos forem nulos, status é Collecting."""
        self.metadata.min_interval = None
        self.metadata.save()
        self._create_event(days_ago=10)
        result = PredictionService.get_prediction(self.monster, self.world)
        assert result["status_code"] == PredictionStatus.COLLECTING.value

    def test_translation_label_is_present(self) -> None:
        """Garante que o label traduzido está sendo retornado."""
        self._create_event(days_ago=5)
        result = PredictionService.get_prediction(self.monster, self.world)
        # Verifica se o texto traduzido (label) não é igual à chave do enum
        assert result["status"] == str(PredictionStatus.NO_CHANCE.label)

    def test_status_collecting_no_metadata_record(self) -> None:
        """Garante status COLLECTING se o registro de metadados nem existir."""
        # Criamos um monstro novo sem criar o MonsterMetadata para ele
        new_monster = Monster.objects.create(name="Morgaroth")
        result = PredictionService.get_prediction(new_monster, self.world)

        assert result["status_code"] == PredictionStatus.COLLECTING.value
        assert result["chance_percentage"] == 0.0
