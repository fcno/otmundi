from datetime import timedelta

import pytest
from django.utils import timezone

from apps.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.killstats.services.metadata_learning_service import MetadataLearningService
from apps.monsters.models.monster import Monster
from apps.monsters.models.monster_metadata import MonsterMetadata
from apps.worlds.models.world import World


@pytest.mark.django_db
class TestMetadataLearningService:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.monster = Monster.objects.create(name="ferumbras", is_active=True)
        self.world_a = World.objects.create(name="antica")
        self.world_b = World.objects.create(name="belobra")
        self.now = timezone.now()

    def _create_event(self, world: World, days_ago: int) -> None:
        MonsterSpawnEvent.objects.create(
            monster=self.monster,
            world=world,
            timestamp=self.now - timedelta(days=days_ago),
        )

    def test_learning_from_multiple_worlds(self) -> None:
        """Cenário: Antica tem janela de 15 dias, Belobra registra 12 dias. O global deve ser 12-15."""
        # Mundo A: Spawn hoje e há 15 dias (Intervalo 15)
        self._create_event(self.world_a, 0)
        self._create_event(self.world_a, 15)

        # Mundo B: Spawn hoje e há 12 dias (Intervalo 12)
        self._create_event(self.world_b, 0)
        self._create_event(self.world_b, 12)

        MetadataLearningService.recalibrate_monster(self.monster)

        metadata = MonsterMetadata.objects.get(monster=self.monster)
        assert metadata.min_interval == 12
        assert metadata.max_interval == 15

    def test_metadata_dynamic_creation(self) -> None:
        """Verifica se o serviço cria o MonsterMetadata se ele não existir."""
        assert MonsterMetadata.objects.filter(monster=self.monster).count() == 0

        self._create_event(self.world_a, 0)
        self._create_event(self.world_a, 10)

        MetadataLearningService.recalibrate_monster(self.monster)
        assert MonsterMetadata.objects.filter(monster=self.monster).exists()

    def test_no_regression_on_wider_knowledge(self) -> None:
        """Garante que o conhecimento não 'encolha' se dados novos forem menos extremos."""
        # Já sabemos que a janela é 5-20
        MonsterMetadata.objects.create(
            monster=self.monster, min_interval=5, max_interval=20
        )

        # Novo dado observado: 10 dias (está dentro da janela, não deve mudar nada)
        self._create_event(self.world_a, 0)
        self._create_event(self.world_a, 10)

        MetadataLearningService.recalibrate_monster(self.monster)

        metadata = MonsterMetadata.objects.get(monster=self.monster)
        assert metadata.min_interval == 5
        assert metadata.max_interval == 20

    def test_full_recalibration_batch(self) -> None:
        """Testa o processamento em lote para todos os monstros."""
        monster2 = Monster.objects.create(name="orshabaal", is_active=True)
        self._create_event(self.world_a, 0)  # Ferumbras
        self._create_event(self.world_a, 10)

        # Monster 2: Intervalo de 7 dias
        MonsterSpawnEvent.objects.create(
            monster=monster2, world=self.world_a, timestamp=self.now
        )
        MonsterSpawnEvent.objects.create(
            monster=monster2, world=self.world_a, timestamp=self.now - timedelta(days=7)
        )

        MetadataLearningService.full_recalibration()

        assert MonsterMetadata.objects.get(monster=self.monster).min_interval == 10
        assert MonsterMetadata.objects.get(monster=monster2).min_interval == 7

    def test_cold_start_behavior(self) -> None:
        """
        Garante que o sistema se comporta corretamente do zero:
        1. Primeira kill: Não cria metadados (falta de dados comparativos).
        2. Segunda kill: Cria metadados com min/max idênticos.
        """
        # 1. Primeira Kill
        self._create_event(self.world_a, 20)
        MetadataLearningService.recalibrate_monster(self.monster)
        assert not MonsterMetadata.objects.filter(monster=self.monster).exists()

        # 2. Segunda Kill (Hoje)
        self._create_event(self.world_a, 0)
        MetadataLearningService.recalibrate_monster(self.monster)

        assert MonsterMetadata.objects.filter(monster=self.monster).exists()

        metadata = MonsterMetadata.objects.get(monster=self.monster)
        # O único intervalo observado é de 20 dias
        assert metadata.min_interval == 20
        assert metadata.max_interval == 20
