import pytest

from ingestion.services.validators.base import ValidationError
from ingestion.services.validators.integers import validate_integer
from django.utils.translation import activate

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