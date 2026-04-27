from django.conf import settings
from django.db import models
from django.db.models.manager import Manager
from django.utils.translation import gettext_lazy as _

from apps.monsters.models.monster import Monster


class UserMonsterPreference(models.Model):
    """
    Armazena as preferências individuais de visualização de cada usuário.
    """

    objects: Manager["UserMonsterPreference"] = Manager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="monster_preferences",
        verbose_name=_("user"),
    )
    monster = models.ForeignKey(
        Monster,
        on_delete=models.CASCADE,
        related_name="user_preferences",
        verbose_name=_("monster"),
    )
    is_hidden = models.BooleanField(
        _("is hidden"),
        default=False,
        help_text=_("If True, user won't see this monster by default."),
    )
    is_favorite = models.BooleanField(
        _("is favorite"),
        default=False,
        help_text=_("If True, this monster will be pinned to the top."),
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("user monster preference")
        verbose_name_plural = _("user monster preferences")
        unique_together = ("user", "monster")

    def __str__(self) -> str:
        return _("{username} preferences for {monster}").format(
            username=self.user.username, monster=self.monster.name
        )
