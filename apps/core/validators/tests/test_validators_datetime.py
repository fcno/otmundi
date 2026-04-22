# apps/core/validators/tests/test_validators_datetime.py
import pytest

from apps.core.validators.base import ValidationError
from apps.core.validators.datetime import validate_datetime


def test_valid_datetime_with_z() -> None:
    validator = validate_datetime(field="captured_at")
    validator("2026-04-19T14:33:00Z")


def test_valid_datetime_with_offset() -> None:
    validator = validate_datetime(field="captured_at")
    validator("2026-04-19T14:33:00+00:00")


def test_invalid_datetime_without_timezone() -> None:
    validator = validate_datetime(field="captured_at")

    with pytest.raises(ValidationError) as exc:
        validator("2026-04-19T14:33:00")

    assert "timezone" in str(exc.value).lower()


def test_invalid_datetime_format() -> None:
    validator = validate_datetime(field="captured_at")

    with pytest.raises(ValidationError):
        validator("invalid-date")


def test_invalid_datetime_type() -> None:
    validator = validate_datetime(field="captured_at")

    with pytest.raises(ValidationError):
        validator(123)


def test_invalid_empty_string() -> None:
    validator = validate_datetime(field="captured_at")

    with pytest.raises(ValidationError):
        validator("")
