from django.db import models

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
        constraints = [
            models.UniqueConstraint(
                fields=["snapshot", "monster"],
                name="unique_killstat_per_snapshot_monster",
            )
        ]

    def __str__(self) -> str:
        return f"{self.monster.name} ({self.snapshot.captured_at})"
