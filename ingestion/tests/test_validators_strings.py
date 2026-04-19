import pytest

from ingestion.services.validators.base import ValidationError
from ingestion.services.validators.strings import validate_string


def test_valid_string() -> None:
    validate_string("Dragon")


def test_optional_none() -> None:
    validate_string(None, required=False)


def test_empty_required() -> None:
    with pytest.raises(ValidationError):
        validate_string("")


def test_none_required() -> None:
    with pytest.raises(ValidationError):
        validate_string(None)


def test_not_string() -> None:
    with pytest.raises(ValidationError):
        validate_string(123)
