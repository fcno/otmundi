from apps.core.normalizers.strings import normalize_string


def test_normalize_string_basic() -> None:
    assert normalize_string("Dragon") == "dragon"


def test_normalize_string_strip() -> None:
    assert normalize_string("  Dragon  ") == "dragon"


def test_normalize_string_empty() -> None:
    assert normalize_string("") == ""


def test_normalize_string_spaces_only() -> None:
    assert normalize_string("   ") == ""
