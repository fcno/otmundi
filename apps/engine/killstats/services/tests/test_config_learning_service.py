from datetime import timedelta

import pytest
from django.utils import timezone

from apps.engine.killstats.models.creature_config import CreatureConfig
from apps.engine.killstats.models.creature_spawn_event import CreatureSpawnEvent
from apps.engine.killstats.services.config_learning_service import (
    ConfigLearningService,
)
from apps.game_data.creatures.models.creature import Creature
from apps.game_data.worlds.models.world import World


@pytest.mark.django_db
class TestConfigLearningService:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.creature = Creature.objects.create(name="ferumbras")
        CreatureConfig.objects.create(creature=self.creature, is_active=True)
        self.world_a = World.objects.create(name="antica")
        self.world_b = World.objects.create(name="belobra")
        self.now = timezone.now()

    def _create_event(
        self, world: World, days_ago: int, creature: Creature | None = None
    ) -> None:
        target_creature = creature or self.creature
        CreatureSpawnEvent.objects.create(
            creature=target_creature,
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

        ConfigLearningService.recalibrate_creature(self.creature)

        config = CreatureConfig.objects.get(creature=self.creature)
        assert config.min_interval == 12
        assert config.max_interval == 15

    def test_config_dynamic_creation(self) -> None:
        """Verifica se o serviço cria o CreatureConfig se ele não existir ao recalibrar."""
        # 1. Criamos uma criatura nova que NÃO tem config (não usamos o self.creature)
        new_creature = Creature.objects.create(name="ghazbaran")

        # Garantimos que ela nasceu sem config
        assert not CreatureConfig.objects.filter(creature=new_creature).exists()

        # 2. Simulamos eventos para esta criatura nova
        CreatureSpawnEvent.objects.create(
            creature=new_creature, world=self.world_a, timestamp=self.now
        )
        CreatureSpawnEvent.objects.create(
            creature=new_creature,
            world=self.world_a,
            timestamp=self.now - timedelta(days=10),
        )

        # 3. O serviço deve detectar a ausência e criar a config automaticamente
        ConfigLearningService.recalibrate_creature(new_creature)

        # 4. Verificação final
        assert CreatureConfig.objects.filter(creature=new_creature).exists()
        config = CreatureConfig.objects.get(creature=new_creature)
        assert (
            config.is_active is False
        )  # Por padrão, criação dinâmica deve ser inativa

    def test_no_regression_on_wider_knowledge(self) -> None:
        """Garante que o conhecimento não 'encolha' se dados novos forem menos extremos."""
        # 1. Em vez de criar, pegamos a config que o setup já criou
        config = CreatureConfig.objects.get(creature=self.creature)
        config.min_interval = 5
        config.max_interval = 20
        config.is_active = True
        config.save()

        # 2. Novo dado observado: 10 dias (dentro da janela 5-20)
        self._create_event(self.world_a, 0)
        self._create_event(self.world_a, 10)

        # 3. Recalibramos
        ConfigLearningService.recalibrate_creature(self.creature)

        # 4. Verificamos se os valores CONFIRMADOS (5 e 20) foram preservados
        config.refresh_from_db()
        assert config.min_interval == 5
        assert config.max_interval == 20

    def test_full_recalibration_batch(self) -> None:
        """Testa o processamento em lote para todas as criaturas."""
        creature2 = Creature.objects.create(name="orshabaal")
        CreatureConfig.objects.create(creature=creature2, is_active=True)
        self._create_event(self.world_a, 0)  # Ferumbras
        self._create_event(self.world_a, 10)

        # creature 2: Intervalo de 7 dias
        CreatureSpawnEvent.objects.create(
            creature=creature2, world=self.world_a, timestamp=self.now
        )
        CreatureSpawnEvent.objects.create(
            creature=creature2,
            world=self.world_a,
            timestamp=self.now - timedelta(days=7),
        )

        ConfigLearningService.full_recalibration()

        assert CreatureConfig.objects.get(creature=self.creature).min_interval == 10
        assert CreatureConfig.objects.get(creature=creature2).min_interval == 7

    def test_cold_start_behavior(self) -> None:
        """
        Garante que o sistema se comporta corretamente do zero:
        1. Primeira kill: Não cria metadados (falta de dados comparativos).
        2. Segunda kill: Cria metadados com min/max idênticos.
        """
        # 1. Criamos uma criatura nova sem NENHUMA config vinculada
        cold_creature = Creature.objects.create(name="ferumbras-cold-start")

        # 1. Primeira Kill (20 dias atrás)
        self._create_event(self.world_a, 20, creature=cold_creature)
        ConfigLearningService.recalibrate_creature(cold_creature)

        # Sem dois eventos, não há intervalo, logo não há config.
        assert not CreatureConfig.objects.filter(creature=cold_creature).exists()

        # 2. Segunda Kill
        self._create_event(self.world_a, 0, creature=cold_creature)
        ConfigLearningService.recalibrate_creature(cold_creature)

        # Verificação final
        assert CreatureConfig.objects.filter(creature=cold_creature).exists()
        config = CreatureConfig.objects.get(creature=cold_creature)

        # O único intervalo observado entre as duas kills é de 20 dias
        assert config.min_interval == 20
        assert config.max_interval == 20
        assert (
            config.is_active is False
        )  # Criado automaticamente pelo serviço, deve vir inativo
