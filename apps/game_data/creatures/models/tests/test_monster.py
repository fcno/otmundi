import pytest
from django.db.utils import IntegrityError

from apps.game_data.creatures.models import Creature


@pytest.mark.django_db
def test_create_creature() -> None:
    creature = Creature.objects.create(name="  Dragon  ")
    assert creature.name == "dragon"  # Normalização do model


@pytest.mark.django_db
def test_unique_name() -> None:
    Creature.objects.create(name="Dragon")
    with pytest.raises(IntegrityError):
        Creature.objects.create(name="DRAGON")  # Normalização garante a unicidade real
