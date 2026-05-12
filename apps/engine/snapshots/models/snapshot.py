from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.game_data.worlds.models.world import World


class Snapshot(models.Model):
    # snapshot_id é a chave de unicidade técnica do arquivo
    snapshot_id = models.CharField(max_length=100, unique=True, db_index=True)
    world = models.ForeignKey(World, on_delete=models.CASCADE, related_name="snapshots")
    captured_at = models.DateTimeField()
    source_file = models.CharField(max_length=255)

    class Meta:
        app_label = "snapshots"
        verbose_name = _("snapshot")
        verbose_name_plural = _("snapshots")

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
        return _("{world_name} - {captured_at}").format(
            world_name=self.world.name, captured_at=self.captured_at
        )
