from django.db import models

from monsters.models.monster import Monster
from snapshots.models.snapshot import Snapshot


class KillStat(models.Model):
    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE)
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)

    last_day_players_killed = models.IntegerField()
    last_day_monsters_killed = models.IntegerField()

    last_7_days_players_killed = models.IntegerField()
    last_7_days_monsters_killed = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["snapshot", "monster"],
                name="unique_killstat_per_snapshot_monster",
            )
        ]

    def __str__(self) -> str:
        return self.monster.name
