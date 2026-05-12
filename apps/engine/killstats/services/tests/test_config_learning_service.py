from datetime import timedelta

import pytest
from django.utils import timezone

from apps.engine.killstats.models.monster_config import MonsterConfig
from apps.engine.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.engine.killstats.services.config_learning_service import (
    ConfigLearningService,
)
from apps.game_data.monsters.models.monster import Monster
from apps.game_data.worlds.models.world import World


@pytest.mark.django_db
class TestConfigLearningService:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.monster = Monster.objects.create(name="ferumbras")
        MonsterConfig.objects.create(monster=self.monster, is_active=True)
        self.world_a = World.objects.create(name="antica")
        self.world_b = World.objects.create(name="belobra")
        self.now = timezone.now()

    def _create_event(
        self, world: World, days_ago: int, monster: Monster | None = None
    ) -> None:
        target_monster = monster or self.monster
        MonsterSpawnEvent.objects.create(
            monster=target_monster,
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

        ConfigLearningService.recalibrate_monster(self.monster)

        config = MonsterConfig.objects.get(monster=self.monster)
        assert config.min_interval == 12
        assert config.max_interval == 15

    def test_config_dynamic_creation(self) -> None:
        """Verifica se o serviço cria o MonsterConfig se ele não existir ao recalibrar."""
        # 1. Criamos um monstro novo que NÃO tem config (não usamos o self.monster)
        new_monster = Monster.objects.create(name="ghazbaran")

        # Garantimos que ele nasceu sem config
        assert not MonsterConfig.objects.filter(monster=new_monster).exists()

        # 2. Simulamos eventos para este monstro novo
        MonsterSpawnEvent.objects.create(
            monster=new_monster, world=self.world_a, timestamp=self.now
        )
        MonsterSpawnEvent.objects.create(
            monster=new_monster,
            world=self.world_a,
            timestamp=self.now - timedelta(days=10),
        )

        # 3. O serviço deve detectar a ausência e criar a config automaticamente
        ConfigLearningService.recalibrate_monster(new_monster)

        # 4. Verificação final
        assert MonsterConfig.objects.filter(monster=new_monster).exists()
        config = MonsterConfig.objects.get(monster=new_monster)
        assert (
            config.is_active is False
        )  # Por padrão, criação dinâmica deve ser inativa

    def test_no_regression_on_wider_knowledge(self) -> None:
        """Garante que o conhecimento não 'encolha' se dados novos forem menos extremos."""
        # 1. Em vez de criar, pegamos a config que o setup já criou
        config = MonsterConfig.objects.get(monster=self.monster)
        config.min_interval = 5
        config.max_interval = 20
        config.is_active = True
        config.save()

        # 2. Novo dado observado: 10 dias (dentro da janela 5-20)
        self._create_event(self.world_a, 0)
        self._create_event(self.world_a, 10)

        # 3. Recalibramos
        ConfigLearningService.recalibrate_monster(self.monster)

        # 4. Verificamos se os valores CONFIRMADOS (5 e 20) foram preservados
        config.refresh_from_db()
        assert config.min_interval == 5
        assert config.max_interval == 20

    def test_full_recalibration_batch(self) -> None:
        """Testa o processamento em lote para todos os monstros."""
        monster2 = Monster.objects.create(name="orshabaal")
        MonsterConfig.objects.create(monster=monster2, is_active=True)
        self._create_event(self.world_a, 0)  # Ferumbras
        self._create_event(self.world_a, 10)

        # Monster 2: Intervalo de 7 dias
        MonsterSpawnEvent.objects.create(
            monster=monster2, world=self.world_a, timestamp=self.now
        )
        MonsterSpawnEvent.objects.create(
            monster=monster2, world=self.world_a, timestamp=self.now - timedelta(days=7)
        )

        ConfigLearningService.full_recalibration()

        assert MonsterConfig.objects.get(monster=self.monster).min_interval == 10
        assert MonsterConfig.objects.get(monster=monster2).min_interval == 7

    def test_cold_start_behavior(self) -> None:
        """
        Garante que o sistema se comporta corretamente do zero:
        1. Primeira kill: Não cria metadados (falta de dados comparativos).
        2. Segunda kill: Cria metadados com min/max idênticos.
        """
        # 1. Criamos um monstro novo sem NENHUMA config vinculada
        cold_monster = Monster.objects.create(name="ferumbras-cold-start")

        # 1. Primeira Kill (20 dias atrás)
        self._create_event(self.world_a, 20, monster=cold_monster)
        ConfigLearningService.recalibrate_monster(cold_monster)

        # Sem dois eventos, não há intervalo, logo não há config.
        assert not MonsterConfig.objects.filter(monster=cold_monster).exists()

        # 2. Segunda Kill
        self._create_event(self.world_a, 0, monster=cold_monster)
        ConfigLearningService.recalibrate_monster(cold_monster)

        # Verificação final
        assert MonsterConfig.objects.filter(monster=cold_monster).exists()
        config = MonsterConfig.objects.get(monster=cold_monster)

        # O único intervalo observado entre as duas kills é de 20 dias
        assert config.min_interval == 20
        assert config.max_interval == 20
        assert (
            config.is_active is False
        )  # Criado automaticamente pelo serviço, deve vir inativo
