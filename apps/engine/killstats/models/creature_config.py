from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.game_data.creatures.models.creature import Creature


class CreatureConfig(models.Model):
    """
    Armazena os parâmetros de predição e configurações validadas para uma criatura.
    Une o aprendizado automático (suggested) com a curadoria manual (confirmed).
    """

    creature = models.OneToOneField(
        Creature,
        on_delete=models.CASCADE,
        related_name="config",
        verbose_name=_("creature"),
    )

    # Restrição: Mínimo 1 dia via validador nativo
    min_interval = models.PositiveIntegerField(
        _("confirmed minimum interval"),
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text=_("The lower bound of the spawn window validated by a human."),
    )
    max_interval = models.PositiveIntegerField(
        _("confirmed maximum interval"),
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text=_("The upper bound of the spawn window validated by an admin."),
    )
    is_active = models.BooleanField(
        default=False,
        help_text=_(
            "Defines whether the creature will be displayed on the creature monitor."
        ),
    )

    # Campos de Auditoria
    validated_at = models.DateTimeField(_("validated at"), null=True, blank=True)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_config",
        verbose_name=_("validated by"),
    )

    class Meta:
        app_label = "killstats"
        verbose_name = _("creature config")
        verbose_name_plural = _("creature configs")

    def __str__(self) -> str:
        status = _("Active") if self.is_active else _("Inactive")
        min_val = self.min_interval if self.min_interval is not None else "?"
        max_val = self.max_interval if self.max_interval is not None else "?"

        return _("{status} | Config: {creature} ({min}-{max} days)").format(
            status=status, creature=self.creature.name, min=min_val, max=max_val
        )
