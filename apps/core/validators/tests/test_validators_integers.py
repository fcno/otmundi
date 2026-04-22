import pytest

from apps.core.validators.base import ValidationError
from apps.core.validators.integers import validate_integer


def test_valid_int() -> None:
    validator = validate_integer(field="age")
    validator(123)


def test_valid_string_int() -> None:
    validator = validate_integer(field="age")
    validator("123")


def test_invalid_with_spaces() -> None:
    validator = validate_integer(field="age")
    with pytest.raises(ValidationError):
        validator(" 123 ")


def test_invalid_with_comma() -> None:
    validator = validate_integer(field="age")
    with pytest.raises(ValidationError):
        validator("1,234")


def test_invalid_with_dot() -> None:
    validator = validate_integer(field="age")
    with pytest.raises(ValidationError):
        validator("1.234")


def test_invalid_alpha() -> None:
    validator = validate_integer(field="age")
    with pytest.raises(ValidationError):
        validator("abc")


def test_invalid_empty_string() -> None:
    validator = validate_integer(field="age")
    with pytest.raises(ValidationError):
        validator("")


def test_invalid_none() -> None:
    validator = validate_integer(field="age")
    with pytest.raises(ValidationError):
        validator(None)