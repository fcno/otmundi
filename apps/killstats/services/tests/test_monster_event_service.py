import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.killstats.services.monster_event_service import MonsterEventService
from apps.monsters.models.monster import Monster

User = get_user_model()


@pytest.mark.django_db
class TestMonsterSpawnEvent:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.monster = Monster.objects.create(name="Orshabaal")
        self.user = User.objects.create_user(username="mod_test", password="123")

    def test_spawn_event_full_creation(self) -> None:
        """Testa a criação completa com todos os campos preenchidos."""
        now = timezone.now()
        event = MonsterSpawnEvent.objects.create(
            monster=self.monster, timestamp=now, is_puff=True, reported_by=self.user
        )
        assert event.monster == self.monster
        assert event.timestamp == now
        assert event.is_puff is True
        assert event.reported_by == self.user

    def test_service_create_manual_puff(self) -> None:
        """Valida que o serviço de domínio cria corretamente um Puff via Web."""
        now = timezone.now()
        event = MonsterEventService.create_manual_puff(
            monster=self.monster, timestamp=now, reported_by_id=self.user.id
        )

        assert event.is_puff is True
        assert event.reported_by == self.user
        assert event.timestamp == now

    def test_spawn_event_defaults(self) -> None:
        """Testa se os valores padrão (is_puff=False) são aplicados."""
        event = MonsterSpawnEvent.objects.create(
            monster=self.monster, timestamp=timezone.now()
        )
        assert event.is_puff is False
        assert event.reported_by is None

    def test_str_representation_kill(self) -> None:
        """Testa o método __str__ para um evento de morte (Kill)."""
        event = MonsterSpawnEvent(
            monster=self.monster, timestamp=timezone.now(), is_puff=False
        )
        assert "Kill" in str(event)
        assert "orshabaal" in str(event)

    def test_str_representation_puff(self) -> None:
        """Testa o método __str__ para um evento de desaparecimento (Puff)."""
        event = MonsterSpawnEvent(
            monster=self.monster, timestamp=timezone.now(), is_puff=True
        )
        assert "Puff" in str(event)

    def test_cascade_on_monster_delete(self) -> None:
        """Caso de borda: O evento deve ser removido se o monstro for deletado."""
        MonsterSpawnEvent.objects.create(monster=self.monster, timestamp=timezone.now())
        self.monster.delete()
        assert MonsterSpawnEvent.objects.count() == 0

    def test_null_reported_by_on_user_delete(self) -> None:
        """Caso de borda: O evento deve permanecer (SET_NULL) se o usuário for deletado."""
        event = MonsterSpawnEvent.objects.create(
            monster=self.monster, timestamp=timezone.now(), reported_by=self.user
        )
        self.user.delete()
        event.refresh_from_db()
        assert event.reported_by is None
