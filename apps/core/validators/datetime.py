# apps/core/validators/datetime.py
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_naive
from django.utils.translation import gettext_lazy as _

from .base import ValidationError
from .types import Validator


def validate_datetime(*, field: str) -> Validator:
    def _validator(value: object) -> None:
        if not isinstance(value, str):
            raise ValidationError(
                _("The field '{field}' must be a datetime string.").format(field=field)
            )

        dt = parse_datetime(value)

        if dt is None:
            raise ValidationError(
                _("The field '{field}' has an invalid datetime.").format(field=field)
            )

        if is_naive(dt):
            raise ValidationError(
                _("The field '{field}' must include timezone.").format(field=field)
            )

    return _validator
