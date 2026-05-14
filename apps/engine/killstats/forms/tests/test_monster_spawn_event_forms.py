import pytest
from django.utils import timezone

from apps.engine.killstats.forms.monster_spawn_event_forms import MonsterSpawnEventForm
from apps.game_data.monsters.models.monster import Monster
from apps.game_data.worlds.models.world import World


@pytest.mark.django_db
class TestMonsterSpawnEventForm:
    def test_form_valid_data(self) -> None:
        """Dados válidos devem permitir a criação."""
        monster = Monster.objects.create(name="ferumbras")
        world = World.objects.create(name="antica")

        data = {
            "monster": monster.id,
            "world": world.id,
            "timestamp": timezone.now(),
            "is_puff": False,
        }
        form = MonsterSpawnEventForm(data=data)
        assert form.is_valid() is True

    def test_form_missing_required_fields(self) -> None:
        """Campos obrigatórios ausentes devem invalidar o form."""
        form = MonsterSpawnEventForm(data={})
        assert form.is_valid() is False
        assert "monster" in form.errors
        assert "world" in form.errors
        assert "timestamp" in form.errors
