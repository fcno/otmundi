# apps/core/validators/tests/test_validators_strings.py
import pytest

from apps.core.validators.base import ValidationError
from apps.core.validators.strings import validate_string


def test_valid_string() -> None:
    validator = validate_string(field="name")
    validator("Dragon")


def test_empty_string() -> None:
    validator = validate_string(field="name")
    with pytest.raises(ValidationError):
        validator("")


def test_string_with_spaces_only_invalid() -> None:
    validator = validate_string(field="name")
    with pytest.raises(ValidationError):
        validator("     ")


def test_none_invalid() -> None:
    validator = validate_string(field="name")
    with pytest.raises(ValidationError):
        validator(None)


def test_not_string() -> None:
    validator = validate_string(field="name")
    with pytest.raises(ValidationError):
        validator(123)