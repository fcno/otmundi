from typing import Any


def sanitize_data(data: Any) -> Any:
    """
    Simula o TrimStrings e ConvertEmptyStringsToNull do Laravel.
    Processa dicionários e listas recursivamente.
    """
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}

    if isinstance(data, list):
        return [sanitize_data(i) for i in data]

    if isinstance(data, str):
        trimmed = data.strip()
        # Se após o trim a string for vazia, retorna None (Null)
        return None if trimmed == "" else trimmed

    return data
