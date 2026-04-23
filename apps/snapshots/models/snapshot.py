from django.db import models
from apps.worlds.models.world import World

class Snapshot(models.Model):
    # snapshot_id agora é a chave de unicidade técnica do arquivo
    snapshot_id = models.CharField(max_length=100, unique=True, db_index=True)
    world = models.ForeignKey(
        World, 
        on_delete=models.CASCADE, 
        related_name="snapshots"
    )
    captured_at = models.DateTimeField()
    source_file = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["world", "captured_at"],
                name="unique_snapshot_per_world_datetime",
            )
        ]
        indexes = [
            models.Index(fields=["captured_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.world.name} - {self.captured_at}"
