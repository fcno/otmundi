import pytest

from apps.core.validators.base import ValidationError
from apps.core.validators.datetime import validate_datetime


def test_valid_datetime_with_z() -> None:
    validate_datetime("2026-04-19T14:33:00Z")


def test_valid_datetime_with_offset() -> None:
    validate_datetime("2026-04-19T14:33:00+00:00")


def test_invalid_datetime_without_timezone() -> None:
    with pytest.raises(ValidationError) as exc:
        validate_datetime("2026-04-19T14:33:00")

    assert "timezone" in str(exc.value).lower()


def test_invalid_datetime_format() -> None:
    with pytest.raises(ValidationError):
        validate_datetime("invalid-date")


def test_invalid_datetime_type() -> None:
    with pytest.raises(ValidationError):
        validate_datetime(123)


def test_invalid_empty_string() -> None:
    with pytest.raises(ValidationError):
        validate_datetime("")
