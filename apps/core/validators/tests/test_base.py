import pytest

from apps.core.validators.base import ValidationError


def test_validation_error_is_exception() -> None:
    assert issubclass(ValidationError, Exception)


def test_validation_error_can_be_raised() -> None:
    with pytest.raises(ValidationError):
        raise ValidationError("error")