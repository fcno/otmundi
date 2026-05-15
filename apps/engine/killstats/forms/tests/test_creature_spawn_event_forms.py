import pytest
from django.utils import timezone

from apps.engine.killstats.forms.creature_spawn_event_forms import (
    CreatureSpawnEventForm,
)
from apps.game_data.creatures.models.creature import Creature
from apps.game_data.worlds.models.world import World


@pytest.mark.django_db
class TestCreatureSpawnEventForm:
    def test_form_valid_data(self) -> None:
        """Dados válidos devem permitir a criação."""
        creature = Creature.objects.create(name="ferumbras")
        world = World.objects.create(name="antica")

        data = {
            "creature": creature.id,
            "world": world.id,
            "timestamp": timezone.now(),
            "is_puff": False,
        }
        form = CreatureSpawnEventForm(data=data)
        assert form.is_valid() is True

    def test_form_missing_required_fields(self) -> None:
        """Campos obrigatórios ausentes devem invalidar o form."""
        form = CreatureSpawnEventForm(data={})
        assert form.is_valid() is False
        assert "creature" in form.errors
        assert "world" in form.errors
        assert "timestamp" in form.errors
