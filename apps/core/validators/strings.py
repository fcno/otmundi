# apps/core/validators/strings.py
from django.utils.translation import gettext_lazy as _

from .base import ValidationError
from .types import Validator


def validate_string(*, field: str) -> Validator:
    def _validator(value: object) -> None:
        if not isinstance(value, str):
            raise ValidationError(
                _("The field '{field}' must be a string.").format(field=field)
            )

        if value.strip() == "":
            raise ValidationError(
                _("The field '{field}' cannot be empty.").format(field=field)
            )

    return _validator