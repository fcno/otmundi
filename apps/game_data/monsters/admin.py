from typing import TYPE_CHECKING

from django.contrib import admin

from ...engine.killstats.models.monster_config import MonsterConfig

if TYPE_CHECKING:
    # Isso só existe durante a análise do Mypy
    BaseAdmin = admin.ModelAdmin[MonsterConfig]
else:
    # Isso é o que o Django usa em tempo de execução
    BaseAdmin = admin.ModelAdmin


@admin.register(MonsterConfig)
class MonsterConfigAdmin(BaseAdmin):
    list_display = ("monster", "min_interval", "max_interval")
    search_fields = ("monster__name",)
