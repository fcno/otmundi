import pytest

from apps.core.normalizers.integers import normalize_integer


def test_normalize_valid_integer_string() -> None:
    assert normalize_integer("123") == 123


def test_normalize_valid_integer_int() -> None:
    assert normalize_integer(123) == 123


def test_normalize_zero() -> None:
    assert normalize_integer("0") == 0


def test_normalize_large_number() -> None:
    assert normalize_integer("999999") == 999999


def test_normalize_invalid_string() -> None:
    with pytest.raises(ValueError):
        normalize_integer("abc")


def test_normalize_invalid_format() -> None:
    with pytest.raises(ValueError):
        normalize_integer("1.23")