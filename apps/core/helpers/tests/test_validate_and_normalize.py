from datetime import UTC, datetime

import pytest

from apps.core.helpers.validate_and_normalize import validate_and_normalize
from apps.core.normalizers.datetime import normalize_datetime
from apps.core.normalizers.integers import normalize_integer
from apps.core.normalizers.strings import normalize_string
from apps.core.validators.base import ValidationError
from apps.core.validators.datetime import validate_datetime
from apps.core.validators.integers import validate_integer
from apps.core.validators.required import validate_required
from apps.core.validators.strings import validate_string


def test_string_pipeline() -> None:
    result = validate_and_normalize(
        "  ABC  ",
        [validate_string(field="name")],
        normalize_string,
    )
    assert result == "abc"


def test_integer_pipeline() -> None:
    result = validate_and_normalize(
        10,
        [validate_integer(field="age")],
        normalize_integer,
    )
    assert result == 10


def test_datetime_pipeline() -> None:
    result = validate_and_normalize(
        "2026-01-01T00:00:00+00:00",
        [validate_datetime(field="captured_at")],
        normalize_datetime,
    )

    expected = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)

    assert result == expected


def test_multiple_validators_error_on_second() -> None:
    with pytest.raises(ValidationError):
        validate_and_normalize(
            "",  # passa required, falha no string
            [
                validate_required(field="name"),
                validate_string(field="name"),
            ],
            normalize_string,
        )


def test_validation_error_required() -> None:
    with pytest.raises(ValidationError):
        validate_and_normalize(
            None,
            [
                validate_required(field="name"),
                validate_string(field="name"),
            ],
            normalize_string,
        )
