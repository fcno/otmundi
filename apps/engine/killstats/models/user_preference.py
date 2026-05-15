from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.game_data.creatures.models.creature import Creature


class UserKillStatPreference(models.Model):
    """
    Armazena as preferências individuais de visualização de cada usuário.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="creature_preferences",
    )
    creature = models.ForeignKey(
        Creature, on_delete=models.CASCADE, related_name="user_preferences"
    )

    # Flags de visualização
    is_pinned = models.BooleanField(
        default=False, help_text=_("Pinned creatures appear at the top.")
    )
    is_low_priority = models.BooleanField(
        default=False, help_text=_("Low priority creatures appear at the bottom.")
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "killstats"
        verbose_name = _("user creature preference")
        verbose_name_plural = _("user creature preferences")
        unique_together = ("user", "creature")

    def __str__(self) -> str:
        # Normalização da string de exibição para o admin
        return _("{username} preferences for {creature}").format(
            username=self.user.username, creature=self.creature.name
        )
