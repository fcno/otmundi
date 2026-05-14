from datetime import timedelta

import pytest
from django.utils import timezone

from apps.engine.killstats.models.monster_config import MonsterConfig
from apps.engine.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.engine.killstats.services.prediction_service import (
    PredictionService,
    PredictionStatus,
)
from apps.game_data.monsters.models.monster import Monster
from apps.game_data.worlds.models.world import World


@pytest.mark.django_db
class TestPredictionService:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.world = World.objects.create(name="Antica")
        self.monster = Monster.objects.create(name="orshabaal")
        self.now = timezone.now()

        # Janela de 10 a 20 dias (Total de 11 dias possíveis para o cálculo de chance)
        self.config = MonsterConfig.objects.create(
            monster=self.monster, is_active=True, min_interval=10, max_interval=20
        )

    def _create_event(self, days_ago: int, monster: Monster | None = None) -> None:
        """Helper para criar eventos no passado com suporte a monstros opcionais."""
        target_monster = monster or self.monster
        timestamp = self.now - timedelta(days=days_ago)
        MonsterSpawnEvent.objects.create(
            monster=target_monster,
            world=self.world,
            timestamp=timestamp,
        )

    def test_status_collecting_data_no_event(self) -> None:
        """Caso o monstro nunca tenha sido visto no mundo."""
        result = PredictionService.get_prediction(self.monster, self.world)
        assert result["status_code"] == PredictionStatus.COLLECTING.value
        assert result["chance_percentage"] == 0.0

    def test_status_no_chance(self) -> None:
        """Monstro morreu há 5 dias, janela mínima é 10."""
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
        """Extremo: Passou 20% do limite máximo (20 * 1.2 = 24 dias)."""
        self._create_event(days_ago=25)
        result = PredictionService.get_prediction(self.monster, self.world)
        assert result["status_code"] == PredictionStatus.MISSING.value
        assert result["chance_percentage"] == 0

    def test_config_null_intervals(self) -> None:
        """Garante que se os campos forem nulos, status é Collecting."""
        self.config.min_interval = None
        self.config.save()
        self._create_event(days_ago=10)
        result = PredictionService.get_prediction(self.monster, self.world)
        assert result["status_code"] == PredictionStatus.COLLECTING.value

    def test_translation_label_is_present(self) -> None:
        """Garante que o label traduzido está sendo retornado."""
        self._create_event(days_ago=5)
        result = PredictionService.get_prediction(self.monster, self.world)
        assert result["status"] == str(PredictionStatus.NO_CHANCE.label)

    def test_status_collecting_no_config_record(self) -> None:
        """Garante status COLLECTING se o registro de metadados nem existir."""
        # Nome único para o teste
        new_monster = Monster.objects.create(name="morgaroth-test-service")
        # Não criamos MonsterConfig para ele
        result = PredictionService.get_prediction(new_monster, self.world)

        assert result["status_code"] == PredictionStatus.COLLECTING.value
        assert result["chance_percentage"] == 0.0

    def test_enum_weights_priority_order(self) -> None:
        """Valida que a hierarquia de pesos segue a urgência de exibição (Menor = Topo)."""
        assert PredictionStatus.OVERDUE.weight < PredictionStatus.EXPECTED.weight
        assert PredictionStatus.EXPECTED.weight < PredictionStatus.NO_CHANCE.weight
        assert PredictionStatus.NO_CHANCE.weight < PredictionStatus.MISSING.weight
        assert PredictionStatus.MISSING.weight < PredictionStatus.COLLECTING.weight

    def test_all_enum_weights_are_correct(self) -> None:
        """Valida os valores exatos dos pesos para ordenação multinível."""
        assert PredictionStatus.OVERDUE.weight == 0
        assert PredictionStatus.EXPECTED.weight == 1
        assert PredictionStatus.NO_CHANCE.weight == 2
        assert PredictionStatus.MISSING.weight == 3
        assert PredictionStatus.COLLECTING.weight == 4

    def test_weight_is_consistent_with_status_code(self) -> None:
        """Garante que o acesso dinâmico pelo código mantém o peso correto."""
        for status in PredictionStatus:
            # Simula: PredictionStatus['EXPECTED'].weight
            assert PredictionStatus[status.value].weight == status.weight
