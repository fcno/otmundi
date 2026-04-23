import pytest
from django.db.utils import IntegrityError

from apps.worlds.models.world import World


@pytest.mark.django_db
def test_create_world() -> None:
    world = World.objects.create(external_id="22", name="  Serenian  ")

    assert world.external_id == "22"
    assert world.name == "serenian"


@pytest.mark.django_db
def test_unique_name() -> None:
    World.objects.create(external_id="22", name="Serenian")

    with pytest.raises(IntegrityError):
        # Falha mesmo com casing diferente, pois o model normaliza antes de salvar
        World.objects.create(external_id="23", name="serenian")
