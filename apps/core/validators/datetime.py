from typing import Any

from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _

from .base import ValidationError


def validate_datetime(value: Any) -> None:

    if not isinstance(value, str):
        raise ValidationError(_("Datetime must be a string"))

    dt = parse_datetime(value)

    if dt is None:
        raise ValidationError(_("Invalid datetime"))
