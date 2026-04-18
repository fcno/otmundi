from django.db import models

from worlds.models.world import World


class Snapshot(models.Model):
    snapshot_id = models.CharField(max_length=100, unique=True)

    world = models.ForeignKey(World, on_delete=models.CASCADE)
    captured_at = models.DateTimeField()
    source_file = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["world", "captured_at"],
                name="unique_snapshot_per_world_datetime",
            )
        ]

    def __str__(self) -> str:
        return f"{self.world.name} - {self.captured_at}"
