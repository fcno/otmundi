from django.utils.translation import gettext_lazy as _

from .base import ValidationError


def validate_integer(value: object) -> None:
    if isinstance(value, int):
        return

    if isinstance(value, str) and value.isdigit():
        return

    raise ValidationError(_("Value must be an integer"))
