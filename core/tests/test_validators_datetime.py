import pytest

from core.validators.base import ValidationError
from core.validators.datetime import validate_datetime


def test_valid_iso() -> None:
    validate_datetime("2026-04-18T17:00:00Z")


def test_invalid_format() -> None:
    with pytest.raises(ValidationError):
        validate_datetime("18/04/2026")


def test_invalid_string() -> None:
    with pytest.raises(ValidationError):
        validate_datetime("abc")


def test_not_string() -> None:
    with pytest.raises(ValidationError):
        validate_datetime(123)
