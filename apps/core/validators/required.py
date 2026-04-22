from django.utils.translation import gettext_lazy as _

from .base import ValidationError
from .types import Validator


def validate_required(*, field: str) -> Validator:
    def _validator(value: object) -> None:
        if value is None:
            raise ValidationError(
                _("The field '{field}' is required.").format(field=field)
            )

    return _validator
