from datetime import datetime

import pytest
from django.utils.timezone import is_aware

from apps.core.normalizers.datetime import normalize_datetime


def test_normalize_datetime_returns_datetime() -> None:
    result = normalize_datetime("2026-04-19T14:33:00Z")
    assert isinstance(result, datetime)


def test_normalize_datetime_is_timezone_aware() -> None:
    result = normalize_datetime("2026-04-19T14:33:00Z")
    assert is_aware(result)


def test_normalize_datetime_with_offset() -> None:
    result = normalize_datetime("2026-04-19T14:33:00+00:00")
    assert is_aware(result)


def test_normalize_datetime_preserves_all_fields() -> None:
    result = normalize_datetime("2026-04-19T14:33:00Z")

    assert result.year == 2026
    assert result.month == 4
    assert result.day == 19
    assert result.hour == 14
    assert result.minute == 33
    assert result.second == 0


def test_normalize_invalid_should_fail_fast() -> None:
    with pytest.raises(ValueError):
        normalize_datetime("invalid")
