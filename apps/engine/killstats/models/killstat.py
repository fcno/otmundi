from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.engine.snapshots.models.snapshot import Snapshot
from apps.game_data.monsters.models.monster import Monster


class KillStat(models.Model):
    snapshot = models.ForeignKey(
        Snapshot, on_delete=models.CASCADE, related_name="kill_stats"
    )
    monster = models.ForeignKey(
        Monster, on_delete=models.CASCADE, related_name="kill_stats"
    )

    last_day_players_killed = models.IntegerField()
    last_day_monsters_killed = models.IntegerField()

    last_7_days_players_killed = models.IntegerField()
    last_7_days_monsters_killed = models.IntegerField()

    class Meta:
        app_label = "killstats"
        verbose_name = _("killstat")
        verbose_name_plural = _("killstats")
        constraints = [
            models.UniqueConstraint(
                fields=["snapshot", "monster"],
                name="unique_killstat_per_snapshot_monster",
            )
        ]

    def __str__(self) -> str:
        return _("{monster_name} ({captured_at})").format(
            monster_name=self.monster.name, captured_at=self.snapshot.captured_at
        )
