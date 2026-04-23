from apps.core.helpers.sanitizers import sanitize_data


def test_sanitize_string_trim() -> None:
    """Deve remover espaços no início e fim."""
    assert sanitize_data("  texto  ") == "texto"
    assert sanitize_data("\n texto \t") == "texto"


def test_sanitize_empty_string_to_none() -> None:
    """strings vazias ou só com espaços viram None."""
    assert sanitize_data("") is None
    assert sanitize_data("   ") is None
    assert sanitize_data("\n\t ") is None


def test_sanitize_recursive_dict() -> None:
    """Deve limpar todas as strings dentro de um dicionário aninhado."""
    payload = {
        "name": "  Dragon Lord  ",
        "empty_info": "   ",
        "metadata": {"title": "  BOSS  ", "description": ""},
    }
    expected = {
        "name": "Dragon Lord",
        "empty_info": None,
        "metadata": {"title": "BOSS", "description": None},
    }
    assert sanitize_data(payload) == expected


def test_sanitize_recursive_list() -> None:
    """Deve limpar strings dentro de listas, incluindo listas de dicionários."""
    payload = ["  item 1  ", "", {"key": "  val  "}]
    expected = ["item 1", None, {"key": "val"}]
    assert sanitize_data(payload) == expected


def test_sanitize_preserves_other_types() -> None:
    """Não deve alterar números, booleanos ou None original."""
    assert sanitize_data(123) == 123
    assert sanitize_data(10.5) == 10.5
    assert sanitize_data(True) is True
    assert sanitize_data(None) is None


def test_sanitize_edge_case_deep_nesting() -> None:
    """Caso de borda: Níveis profundos de aninhamento."""
    payload = {"a": {"b": {"c": ["  final  "]}}}
    expected = {"a": {"b": {"c": ["final"]}}}
    assert sanitize_data(payload) == expected


def test_sanitize_complex_payload_killstats() -> None:
    """Teste de integração com a estrutura real"""
    payload = {
        "world": {"id": " 11 ", "name": " Auroria  "},
        "data": [
            {
                "monster": " Dragon ",
                "last_day": {"players_killed": " 5 ", "monsters_killed": 0},
            }
        ],
    }
    expected = {
        "world": {"id": "11", "name": "Auroria"},
        "data": [
            {
                "monster": "Dragon",
                "last_day": {"players_killed": "5", "monsters_killed": 0},
            }
        ],
    }
    assert sanitize_data(payload) == expected
