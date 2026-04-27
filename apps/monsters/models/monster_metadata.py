from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.monsters.models.monster import Monster


class MonsterMetadata(models.Model):
    """
    Armazena os parâmetros de predição para um monstro específico.
    Campos nulos indicam que ainda não há conhecimento prévio sobre o boss.
    Serão ajustados na fase adaptativa.
    """

    monster = models.OneToOneField(
        Monster,
        on_delete=models.CASCADE,
        related_name="metadata",
        verbose_name=_("monster"),
    )
    min_interval = models.PositiveIntegerField(
        _("minimum interval"),
        help_text=_("Minimum days for a new spawn."),
        null=True,
        blank=True,
    )
    max_interval = models.PositiveIntegerField(
        _("maximum interval"),
        help_text=_("Maximum days for a new spawn."),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("monster metadata")
        verbose_name_plural = _("monster metadatas")

    def __str__(self) -> str:
        return _("Config: {monster} ({min}-{max} {days})").format(
            monster=self.monster.name,
            min=self.min_interval if self.min_interval is not None else "?",
            max=self.max_interval if self.max_interval is not None else "?",
            days=_("days"),
        )
