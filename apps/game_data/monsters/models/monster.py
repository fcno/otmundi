from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _


class Monster(models.Model):
    class Meta:
        app_label = "monsters"
        verbose_name = _("monster")
        verbose_name_plural = _("monsters")

    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(
        default=False,
        help_text=_("Define se o monstro será exibido no monitor de bosses."),
    )

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.name:
            self.name = self.name.lower().strip()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
