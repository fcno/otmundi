from typing import Any
from .base import ValidationError


def validate_string(value: Any, *, required: bool = True) -> None:

    if value is None:
        if required:
            raise ValidationError("Value is required")
        return

    if not isinstance(value, str):
        raise ValidationError("Value must be a string")

    if required and value == "":
        raise ValidationError("Value cannot be empty")