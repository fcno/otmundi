import pytest

from apps.core.validators.base import ValidationError
from apps.core.validators.required import validate_required


def test_validate_required_accepts_non_none() -> None:
    validate_required("value", "name")


def test_validate_required_rejects_none() -> None:
    with pytest.raises(ValidationError) as exc:
        validate_required(None, "name")

    assert "required" in str(exc.value)
