from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import ValidationError
from .types import Validator


def validate_unique[T: models.Model](*, model_class: type[T], field: str) -> Validator:
    def _validator(value: Any) -> None:

        # Se o valor for None, o validate_required deve tratar.
        # Se for string vazia, não verificamos unicidade aqui.
        if value is None or value == "":
            return

        # Verifica se já existe um registro com este valor no campo especificado
        exists = model_class._default_manager.filter(**{field: value}).exists()

        if exists:
            raise ValidationError(
                _("The {model} with {field} '{value}' already exists.").format(
                    model=model_class.__name__, field=field, value=value
                )
            )

    return _validator
