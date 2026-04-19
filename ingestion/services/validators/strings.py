from django.utils.translation import gettext_lazy as _
from .base import ValidationError


def validate_string(value: object, required: bool = True) -> None:
    if value is None:
        if required:
            raise ValidationError(_("Value is required"))
        return

    if not isinstance(value, str):
        raise ValidationError(_("Value must be a string"))

    if required and value.strip() == "":
        raise ValidationError(_("Value cannot be empty"))