from typing import TYPE_CHECKING

from django.contrib import admin

from apps.game_data.creatures.models.creature import Creature

if TYPE_CHECKING:
    # Isso só existe durante a análise do Mypy
    BaseAdmin = admin.ModelAdmin[Creature]
else:
    # Isso é o que o Django usa em tempo de execução
    BaseAdmin = admin.ModelAdmin


@admin.register(Creature)
class CreatureAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
