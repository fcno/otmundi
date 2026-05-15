from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.engine.snapshots.models.snapshot import Snapshot
from apps.game_data.creatures.models.creature import Creature


class KillStat(models.Model):
    snapshot = models.ForeignKey(
        Snapshot, on_delete=models.CASCADE, related_name="kill_stats"
    )
    creature = models.ForeignKey(
        Creature, on_delete=models.CASCADE, related_name="kill_stats"
    )

    last_day_players_killed = models.IntegerField()
    last_day_creatures_killed = models.IntegerField()

    last_7_days_players_killed = models.IntegerField()
    last_7_days_creatures_killed = models.IntegerField()

    class Meta:
        app_label = "killstats"
        verbose_name = _("killstat")
        verbose_name_plural = _("killstats")
        constraints = [
            models.UniqueConstraint(
                fields=["snapshot", "creature"],
                name="unique_killstat_per_snapshot_creature",
            )
        ]

    def __str__(self) -> str:
        return _("{creature_name} ({captured_at})").format(
            creature_name=self.creature.name, captured_at=self.snapshot.captured_at
        )
