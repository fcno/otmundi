from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _


class Creature(models.Model):
    class Meta:
        verbose_name = _("creature")
        verbose_name_plural = _("creatures")

    name = models.CharField(max_length=150, unique=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.name:
            self.name = self.name.lower().strip()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
