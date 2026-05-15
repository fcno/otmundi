from typing import TYPE_CHECKING, Any

from django.db.models import QuerySet
from django.views.generic import ListView

from apps.engine.killstats.services.prediction_service import (
    PredictionService,
    PredictionStatus,
)
from apps.game_data.creatures.models import Creature
from apps.game_data.worlds.models.world import World

# Esta lógica faz com que o mypy veja ListView[Creature],
# mas o Python em execução veja apenas ListView.
if TYPE_CHECKING:
    BaseView = ListView[Creature]
else:
    BaseView = ListView


class KillstatMonitorView(BaseView):
    model = Creature
    template_name = "monitor.html"
    context_object_name = "creatures"

    queryset: QuerySet[Creature]

    def get_queryset(self) -> QuerySet[Creature]:
        """
        Retorna apenas as criaturas marcados explicitamente para exibição, consistente com o curator.
        """
        return Creature.objects.filter(config__is_active=True)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # 1. Identifica o mundo e o usuário
        user = self.request.user
        world = World.objects.first()

        if not world:
            context["prediction_enabled"] = False
            return context

        # 2. Mapeia preferências do usuário se estiver autenticado
        user_prefs = {}
        if user.is_authenticated:
            from apps.engine.killstats.models.user_preference import (
                UserKillStatPreference,
            )

            user_prefs = {
                p.creature_id: p
                for p in UserKillStatPreference.objects.filter(user=user)
            }

        # 3. Calcula a predição para cada criatura injetando dados de predição e preferências em cada objeto de criatura
        for creature in context["creatures"]:
            creature.prediction = PredictionService.get_prediction(creature, world)

            # Extrai flags de preferência ou usa False como padrão
            pref = user_prefs.get(creature.id)
            creature.is_pinned = pref.is_pinned if pref else False
            creature.is_low_priority = pref.is_low_priority if pref else False

        # 4. Ordenação multinível usando preferêncis e Enum
        # 1. is_pinned (Topo)
        # 2. is_low_priority (Fundo)
        # 3. Status Weight (Regras de Overdue/Expected/etc)
        # 4. Chance % (Maior primeiro)
        # 5. Nome (Alfabético)
        context["creatures"] = sorted(
            context["creatures"],
            key=lambda b: (
                not b.is_pinned,
                b.is_low_priority,
                PredictionStatus[b.prediction["status_code"]].weight,
                -b.prediction["chance_percentage"],
                b.name,
            ),
        )

        context["current_world"] = world
        context["prediction_enabled"] = True
        return context
