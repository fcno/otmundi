from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.monsters.models.monster import Monster


class UserMonsterPreference(models.Model):
    """
    Armazena as preferências individuais de visualização de cada usuário.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="monster_preferences",
    )
    monster = models.ForeignKey(
        Monster, on_delete=models.CASCADE, related_name="user_preferences"
    )

    # Flags de visualização
    is_pinned = models.BooleanField(
        default=False, help_text=_("Pinned monsters appear at the top.")
    )
    is_low_priority = models.BooleanField(
        default=False, help_text=_("Low priority monsters appear at the bottom.")
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("user monster preference")
        verbose_name_plural = _("user monster preferences")
        unique_together = ("user", "monster")

    def __str__(self) -> str:
        # Normalização da string de exibição para o admin
        return _("{username} preferences for {monster}").format(
            username=self.user.username, monster=self.monster.name
        )
