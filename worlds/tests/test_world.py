import pytest
from django.db.utils import IntegrityError

from worlds.models.world import World


@pytest.mark.django_db
def test_create_world() -> None:
    world = World.objects.create(external_id="22", name="Serenian")

    assert world.external_id == "22"
    assert world.name == "Serenian"


@pytest.mark.django_db
def test_unique_external_id() -> None:
    World.objects.create(external_id="22", name="A")

    with pytest.raises(IntegrityError):
        World.objects.create(external_id="22", name="B")


@pytest.mark.django_db
def test_unique_name() -> None:
    World.objects.create(external_id="22", name="Serenian")

    with pytest.raises(IntegrityError):
        World.objects.create(external_id="23", name="Serenian")
