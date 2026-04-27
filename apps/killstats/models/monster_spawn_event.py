from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import TruncDate
from django.db.models.manager import Manager
from django.utils.translation import gettext_lazy as _

from apps.monsters.models.monster import Monster
from apps.worlds.models.world import World


class MonsterSpawnEvent(models.Model):
    """
    Registra um evento que reinicia a janela de spawn de um monstro.
    Pode ser uma morte (via sistema) ou um 'Puff' (via usuário).
    """

    objects: Manager["MonsterSpawnEvent"] = Manager()

    monster = models.ForeignKey(
        Monster,
        on_delete=models.CASCADE,
        related_name="spawn_events",
        verbose_name=_("monster"),
    )
    timestamp = models.DateTimeField(
        _("event timestamp"), help_text=_("The exact moment the boss died or puffed.")
    )
    is_puff = models.BooleanField(
        _("is puff"),
        default=False,
        help_text=_("True if the boss despawned without being killed."),
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_spawn_events",
        verbose_name=_("reported by"),
        help_text=_("User who manually reported this event via interface."),
    )

    world = models.ForeignKey(
        World,
        on_delete=models.CASCADE,
        related_name="spawn_events",
        verbose_name=_("world"),
    )

    class Meta:
        verbose_name = _("monster spawn event")
        verbose_name_plural = _("monster spawn events")
        ordering = ["-timestamp"]

        constraints = [
            UniqueConstraint(
                TruncDate("timestamp"),
                "monster",
                "world",
                name="unique_monster_spawn_per_day_per_world",
                violation_error_message=_(
                    "This monster already has an event registered for this day on this world."
                ),
            )
        ]

    def __str__(self) -> str:
        # Forçamos a conversão para string para garantir que o .format() receba o tipo correto
        event_type: str = str(_("Puff") if self.is_puff else _("Kill"))
        return _("{monster} - {event_type} @ {timestamp} ({world})").format(
            monster=str(self.monster.name),
            event_type=event_type,
            timestamp=self.timestamp.date().isoformat() if self.timestamp else "",
            world=str(self.world.name),
        )
