import pytest
from django.utils.translation import activate

from apps.core.validators.base import ValidationError
from apps.core.validators.integers import validate_integer


def test_error_in_english() -> None:
    activate("en")

    validator = validate_integer(field="age")

    with pytest.raises(ValidationError) as exc:
        validator("abc")

    assert str(exc.value) == "The field 'age' must be an integer."


def test_error_in_portuguese() -> None:
    activate("pt_BR")

    validator = validate_integer(field="age")

    with pytest.raises(ValidationError) as exc:
        validator("abc")

    assert str(exc.value) == "O campo 'age' deve ser um número inteiro."
