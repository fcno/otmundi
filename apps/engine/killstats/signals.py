from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.engine.killstats.models.creature_spawn_event import CreatureSpawnEvent
from apps.engine.killstats.services.config_learning_service import (
    ConfigLearningService,
)


@receiver(post_save, sender=CreatureSpawnEvent)
def trigger_config_learning(
    sender: Any, instance: CreatureSpawnEvent, created: bool, **kwargs: Any
) -> None:
    """
    Gatilho automático para recalibração de metadados após o registro de um spawn.
    """
    if created:
        ConfigLearningService.recalibrate_creature(instance.creature)
