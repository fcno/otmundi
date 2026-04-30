from typing import TYPE_CHECKING, Any

from django.db.models import QuerySet
from django.views.generic import ListView

from apps.killstats.services.prediction_service import (
    PredictionService,
    PredictionStatus,
)
from apps.monsters.models.monster import Monster
from apps.worlds.models.world import World

# Esta lógica faz com que o mypy veja ListView[Monster],
# mas o Python em execução veja apenas ListView.
if TYPE_CHECKING:
    BaseView = ListView[Monster]
else:
    BaseView = ListView


class BossMonitorView(BaseView):
    model = Monster
    template_name = "monitor.html"
    context_object_name = "bosses"

    queryset: QuerySet[Monster]

    def get_queryset(self) -> QuerySet[Monster]:
        """
        Retorna apenas monstros que possuem metadados configurados (bosses),
        já trazendo os metadados para evitar múltiplas consultas ao banco (N+1).
        """
        return Monster.objects.all()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # 1. Identifica o mundo
        world = World.objects.first()

        if not world:
            context["prediction_enabled"] = False
            return context

        # 2. Calcula a predição para cada boss
        for boss in context["bosses"]:
            boss.prediction = PredictionService.get_prediction(boss, world)

        # 3. Ordenação usando a propriedade do Enum
        context["bosses"] = sorted(
            context["bosses"],
            key=lambda b: (
                # Buscamos o membro do Enum pela string status_code para acessar o .weight
                PredictionStatus[b.prediction["status_code"]].weight,
                -b.prediction["chance_percentage"],
                b.name,
            ),
        )

        context["current_world"] = world
        context["prediction_enabled"] = True
        return context
