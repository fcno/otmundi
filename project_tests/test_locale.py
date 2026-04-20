import pytest
from django.utils.translation import activate

from apps.core.validators.base import ValidationError
from apps.core.validators.integers import validate_integer


def test_error_in_english() -> None:
    activate("en")

    with pytest.raises(ValidationError) as exc:
        validate_integer("abc")

    assert str(exc.value) == "Value must be an integer"


def test_error_in_portuguese() -> None:
    activate("pt_BR")

    with pytest.raises(ValidationError) as exc:
        validate_integer("abc")

    assert str(exc.value) == "Valor deve ser um inteiro"
