from typing import TYPE_CHECKING, Any

from django.contrib import admin
from django.http import HttpRequest

from apps.engine.killstats.models.creature_config import CreatureConfig
from apps.engine.killstats.models.creature_spawn_event import CreatureSpawnEvent
from apps.identity.users.models.user import User

if TYPE_CHECKING:
    # Isso só existe durante a análise do Mypy
    BaseAdmin = admin.ModelAdmin[CreatureConfig]
    EventAdminBase = admin.ModelAdmin[CreatureSpawnEvent]
else:
    # Isso é o que o Django usa em tempo de execução
    BaseAdmin = admin.ModelAdmin
    EventAdminBase = admin.ModelAdmin


@admin.register(CreatureConfig)
class CreatureConfigAdmin(BaseAdmin):
    list_display = ("creature", "min_interval", "max_interval")
    search_fields = ("creature__name",)


@admin.register(CreatureSpawnEvent)
class CreatureSpawnEventAdmin(EventAdminBase):
    list_display = ("creature", "world", "timestamp", "is_puff", "reported_by")
    list_filter = ("is_puff", "world", "creature", "timestamp")
    search_fields = ("creature__name", "world__name", "reported_by__username")
    autocomplete_fields = ("creature", "world")  # Melhora performance com muitos dados
    date_hierarchy = "timestamp"
    readonly_fields = ("reported_by",)

    def save_model(
        self, request: HttpRequest, obj: CreatureSpawnEvent, form: Any, change: Any
    ) -> None:
        if not obj.pk and isinstance(request.user, User):
            obj.reported_by = request.user
        super().save_model(request, obj, form, change)
