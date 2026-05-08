from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _


class World(models.Model):
    class Meta:
        app_label = "worlds"
        verbose_name = _("world")
        verbose_name_plural = _("worlds")

    external_id = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=150, unique=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.name:
            self.name = self.name.lower().strip()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
