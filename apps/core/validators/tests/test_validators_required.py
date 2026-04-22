# apps/core/validators/tests/test_validators_required.py
import pytest

from apps.core.validators.base import ValidationError
from apps.core.validators.required import validate_required


def test_validate_required_accepts_non_none() -> None:
    validator = validate_required(field="name")

    validator("value")


def test_validate_required_rejects_none() -> None:
    validator = validate_required(field="name")

    with pytest.raises(ValidationError) as exc:
        validator(None)

    assert "name" in str(exc.value)
    assert "required" in str(exc.value)
