from typing import TYPE_CHECKING, Any

from django.contrib import admin
from django.http import HttpRequest

from apps.identity.users.models.user import User

from .models.monster_config import MonsterConfig as MonsterConfig
from .models.monster_spawn_event import MonsterSpawnEvent

if TYPE_CHECKING:
    # Isso só existe durante a análise do Mypy
    BaseAdmin = admin.ModelAdmin[MonsterConfig]
    EventAdminBase = admin.ModelAdmin[MonsterSpawnEvent]
else:
    # Isso é o que o Django usa em tempo de execução
    BaseAdmin = admin.ModelAdmin
    EventAdminBase = admin.ModelAdmin


@admin.register(MonsterConfig)
class MonsterConfigAdmin(BaseAdmin):
    list_display = ("monster", "min_interval", "max_interval")
    search_fields = ("monster__name",)


@admin.register(MonsterSpawnEvent)
class MonsterSpawnEventAdmin(EventAdminBase):
    list_display = ("monster", "world", "timestamp", "is_puff", "reported_by")
    list_filter = ("is_puff", "world", "monster", "timestamp")
    search_fields = ("monster__name", "world__name", "reported_by__username")
    autocomplete_fields = ("monster", "world")  # Melhora performance com muitos dados
    date_hierarchy = "timestamp"
    readonly_fields = ("reported_by",)

    def save_model(
        self, request: HttpRequest, obj: MonsterSpawnEvent, form: Any, change: Any
    ) -> None:
        if not obj.pk and isinstance(request.user, User):
            obj.reported_by = request.user
        super().save_model(request, obj, form, change)
