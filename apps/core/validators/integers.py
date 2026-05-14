# apps/core/validators/integers.py
from django.utils.translation import gettext_lazy as _

from apps.core.validators.base import ValidationError
from apps.core.validators.types import Validator


def validate_integer(*, field: str) -> Validator:
    def _validator(value: object) -> None:
        if isinstance(value, int):
            return

        if isinstance(value, str) and value.isdigit():
            return

        raise ValidationError(
            _("The field '{field}' must be an integer.").format(field=field)
        )

    return _validator
