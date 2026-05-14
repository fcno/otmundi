from typing import TYPE_CHECKING

from django.contrib import admin

from apps.game_data.worlds.models.world import World

if TYPE_CHECKING:
    # Isso só existe durante a análise do Mypy
    BaseAdmin = admin.ModelAdmin[World]
else:
    # Isso é o que o Django usa em tempo de execução
    BaseAdmin = admin.ModelAdmin


@admin.register(World)
class WorldAdmin(BaseAdmin):
    search_fields = ("name",)
    list_display = ("name", "external_id")
