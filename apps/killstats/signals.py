from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.killstats.services.metadata_learning_service import MetadataLearningService


@receiver(post_save, sender=MonsterSpawnEvent)
def trigger_metadata_learning(
    sender: Any, instance: MonsterSpawnEvent, created: bool, **kwargs: Any
) -> None:
    """
    Gatilho automático para recalibração de metadados após o registro de um spawn.
    """
    if created:
        MetadataLearningService.recalibrate_monster(instance.monster)
