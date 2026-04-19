from typing import Any
from .base import ValidationError


def validate_integer(value: Any) -> None:

    if isinstance(value, int):
        return

    if isinstance(value, str):
        if value.isdigit():
            return

    raise ValidationError(f"Invalid integer value: {value}")