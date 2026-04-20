from typing import Any

from django.utils.translation import gettext_lazy as _

from .base import ValidationError


def validate_required(value: Any, field_name: str) -> None:
    if value is None:
        raise ValidationError(
            _("The field '{field}' is required.").format(field=field_name)
        )
