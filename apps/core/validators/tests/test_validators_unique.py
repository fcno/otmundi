import pytest

from apps.core.validators.base import ValidationError
from apps.core.validators.unique import validate_unique
from apps.worlds.models.world import World


@pytest.mark.django_db
def test_validate_unique_success() -> None:
    # Não existe nenhum mundo com este nome ainda
    validator = validate_unique(model_class=World, field="name")
    validator("serenian")  # Deve passar sem erros


@pytest.mark.django_db
def test_validate_unique_failure() -> None:
    # Criamos um registro para forçar a falha de unicidade
    World.objects.create(external_id="1", name="serenian")

    validator = validate_unique(model_class=World, field="name")

    with pytest.raises(ValidationError) as exc:
        validator("serenian")

    assert "already exists" in str(exc.value)


@pytest.mark.django_db
def test_validate_unique_ignores_none_and_empty() -> None:
    validator = validate_unique(model_class=World, field="name")

    # Não deve levantar exceção, delegando ao validate_required
    validator(None)
    validator("")
