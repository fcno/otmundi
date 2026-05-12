from datetime import datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.engine.killstats.models.monster_config import MonsterConfig
from apps.engine.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.engine.killstats.services.monster_event_service import MonsterEventService
from apps.game_data.monsters.models.monster import Monster
from apps.game_data.worlds.models.world import World

User = get_user_model()


@pytest.mark.django_db
class TestMonsterSpawnEvent:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.world = World.objects.create(name="Antica")
        self.monster = Monster.objects.create(name="Orshabaal")
        MonsterConfig.objects.create(monster=self.monster, is_active=True)
        self.user = User.objects.create_user(username="mod_test", password="123")

    def test_spawn_event_full_creation(self) -> None:
        """Testa a criação completa com todos os campos preenchidos."""
        now = timezone.now()
        event = MonsterSpawnEvent.objects.create(
            monster=self.monster,
            timestamp=now,
            is_puff=True,
            reported_by=self.user,
            world=self.world,
        )
        assert event.monster == self.monster
        assert event.timestamp == now
        assert event.is_puff is True
        assert event.reported_by == self.user
        assert event.world == self.world

    def test_service_create_manual_puff(self) -> None:
        """Valida que o serviço de domínio cria corretamente um Puff via Web."""
        now = timezone.now()
        event = MonsterEventService.create_manual_puff(
            monster=self.monster,
            timestamp=now,
            reported_by_id=self.user.id,
            world=self.world,
        )

        assert event.is_puff is True
        assert event.reported_by == self.user
        assert event.timestamp == now
        assert event.world == self.world

    def test_spawn_event_defaults(self) -> None:
        """Testa se os valores padrão (is_puff=False) são aplicados."""
        event = MonsterSpawnEvent.objects.create(
            monster=self.monster, timestamp=timezone.now(), world=self.world
        )
        assert event.is_puff is False
        assert event.reported_by is None
        assert event.world == self.world

    def test_str_representation_kill(self) -> None:
        """Testa o método __str__ para um evento de morte (Kill)."""
        event = MonsterSpawnEvent(
            monster=self.monster,
            timestamp=timezone.now(),
            is_puff=False,
            world=self.world,
        )
        assert "Kill" in str(event)
        assert "orshabaal" in str(event)
        assert "antica" in str(event)

    def test_str_representation_puff(self) -> None:
        """Testa o método __str__ para um evento de desaparecimento (Puff)."""
        event = MonsterSpawnEvent(
            monster=self.monster,
            timestamp=timezone.now(),
            is_puff=True,
            world=self.world,
        )
        assert "Puff" in str(event)
        assert "(antica)" in str(event)

    def test_cascade_on_monster_delete(self) -> None:
        """Caso de borda: O evento deve ser removido se o monstro for deletado."""
        MonsterSpawnEvent.objects.create(
            monster=self.monster, timestamp=timezone.now(), world=self.world
        )
        self.monster.delete()
        assert MonsterSpawnEvent.objects.count() == 0

    def test_null_reported_by_on_user_delete(self) -> None:
        """Caso de borda: O evento deve permanecer (SET_NULL) se o usuário for deletado."""
        event = MonsterSpawnEvent.objects.create(
            monster=self.monster,
            timestamp=timezone.now(),
            reported_by=self.user,
            world=self.world,
        )
        self.user.delete()
        event.refresh_from_db()
        assert event.reported_by is None

    def test_calculate_intervals_basic_logic(self) -> None:
        """Testa se calcula corretamente a diferença de dias entre eventos."""
        base_time = datetime(2026, 5, 1)
        # Simula 3 eventos no Mundo 1
        data = {
            1: [
                base_time,
                base_time + timedelta(days=5),
                base_time + timedelta(days=12),
            ]
        }
        intervals = MonsterEventService._calculate_intervals(data)
        # Diferenças: (5-0) = 5, (12-5) = 7
        assert intervals == [5, 7]

    def test_calculate_intervals_multiple_worlds_isolation(self) -> None:
        """Garante que intervalos não são calculados entre mundos diferentes."""
        base_time = datetime(2026, 5, 1)
        data = {
            1: [base_time, base_time + timedelta(days=10)],
            2: [base_time + timedelta(days=2), base_time + timedelta(days=5)],
        }
        intervals = MonsterEventService._calculate_intervals(data)
        # Mundo 1: 10 dias | Mundo 2: 3 dias
        assert 10 in intervals
        assert 3 in intervals
        assert len(intervals) == 2

    def test_calculate_intervals_ignores_single_events(self) -> None:
        """Mundos com apenas um evento não devem gerar intervalos."""
        data = {1: [datetime.now()]}
        intervals = MonsterEventService._calculate_intervals(data)
        assert intervals == []

    def test_calculate_intervals_sorting_robustness(self) -> None:
        """Garante que mesmo que os eventos venham bagunçados, o cálculo é correto."""
        t1 = datetime(2026, 5, 1)
        t2 = datetime(2026, 5, 10)
        # Eventos fora de ordem na lista
        data = {1: [t2, t1]}
        intervals = MonsterEventService._calculate_intervals(data)
        assert intervals == [9]
