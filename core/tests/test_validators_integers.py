import pytest

from core.validators.base import ValidationError
from core.validators.integers import validate_integer


def test_valid_int() -> None:
    validate_integer(123)


def test_valid_string_int() -> None:
    validate_integer("123")


def test_invalid_with_spaces() -> None:
    with pytest.raises(ValidationError):
        validate_integer(" 123 ")


def test_invalid_with_comma() -> None:
    with pytest.raises(ValidationError):
        validate_integer("1,234")


def test_invalid_with_dot() -> None:
    with pytest.raises(ValidationError):
        validate_integer("1.234")


def test_invalid_alpha() -> None:
    with pytest.raises(ValidationError):
        validate_integer("abc")


def test_none() -> None:
    with pytest.raises(ValidationError):
        validate_integer(None)
