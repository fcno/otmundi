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
        Retorna apenas os monstros marcados explicitamente para exibição.
        """
        return Monster.objects.filter(is_active=True)

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
            from apps.preferences.models.user_monster_preference import (
                UserMonsterPreference,
            )

            user_prefs = {
                p.monster_id: p for p in UserMonsterPreference.objects.filter(user=user)
            }

        # 3. Calcula a predição para cada boss injetando dados de predição e preferências em cada objeto de boss
        for boss in context["bosses"]:
            boss.prediction = PredictionService.get_prediction(boss, world)

            # Extrai flags de preferência ou usa False como padrão
            pref = user_prefs.get(boss.id)
            boss.is_pinned = pref.is_pinned if pref else False
            boss.is_low_priority = pref.is_low_priority if pref else False

        # 4. Ordenação multinível usando preferêncis e Enum
        # 1. is_pinned (Topo)
        # 2. is_low_priority (Fundo)
        # 3. Status Weight (Regras de Overdue/Expected/etc)
        # 4. Chance % (Maior primeiro)
        # 5. Nome (Alfabético)
        context["bosses"] = sorted(
            context["bosses"],
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
