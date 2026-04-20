import pytest
from django.db.utils import IntegrityError

from apps.monsters.models.monster import Monster


@pytest.mark.django_db
def test_create_monster() -> None:
    monster = Monster.objects.create(name="Dragon")

    assert monster.name == "Dragon"


@pytest.mark.django_db
def test_unique_name() -> None:
    Monster.objects.create(name="Dragon")

    with pytest.raises(IntegrityError):
        Monster.objects.create(name="Dragon")
