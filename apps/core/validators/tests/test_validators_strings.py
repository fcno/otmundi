import pytest

from apps.core.validators.base import ValidationError
from apps.core.validators.strings import validate_string


def test_valid_string() -> None:
    validator = validate_string(field="name")
    validator("Dragon")


def test_allows_none_and_empty() -> None:
    """
    Deve permitir None e strings vazias, pois a obrigatoriedade
    é delegada ao validate_required e a limpeza ao sanitizer.
    """
    validator = validate_string(field="name")
    validator(None)
    validator("")
    validator("     ")


def test_not_string() -> None:
    validator = validate_string(field="name")
    with pytest.raises(ValidationError):
        validator(123)

    with pytest.raises(ValidationError):
        validator(["not a string"])
