from typing import TYPE_CHECKING

from django.contrib import admin

from .models.monster_metadata import MonsterMetadata

if TYPE_CHECKING:
    # Isso só existe durante a análise do Mypy
    BaseAdmin = admin.ModelAdmin[MonsterMetadata]
else:
    # Isso é o que o Django usa em tempo de execução
    BaseAdmin = admin.ModelAdmin


@admin.register(MonsterMetadata)
class MonsterMetadataAdmin(BaseAdmin):
    list_display = ("monster", "min_interval", "max_interval")
    search_fields = ("monster__name",)
