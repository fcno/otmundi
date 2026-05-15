from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from apps.engine.killstats.models.user_preference import UserKillStatPreference
from apps.game_data.creatures.models import Creature


@login_required
@require_POST
def toggle_creature_preference(request: HttpRequest) -> JsonResponse:
    """
    Alterna preferências de exibição com exclusão mútua condicional.
    """

    assert request.user.is_authenticated

    creature_id = request.POST.get("creature_id")
    action = request.POST.get("action")  # "pin" ou "low_priority"

    creature = get_object_or_404(Creature, id=creature_id)

    # Busca ou cria a preferência para este usuário e criatura
    pref, _ = UserKillStatPreference.objects.get_or_create(
        user=request.user, creature=creature
    )

    if action == "pin":
        pref.is_pinned = not pref.is_pinned
        # Exclusão mútua: se pinou, não pode ser low_priority
        if pref.is_pinned:
            pref.is_low_priority = False

    elif action == "low_priority":
        pref.is_low_priority = not pref.is_low_priority
        # Exclusão mútua: se é baixa prioridade, não pode estar pinado
        if pref.is_low_priority:
            pref.is_pinned = False

    pref.save()

    return JsonResponse(
        {"is_pinned": pref.is_pinned, "is_low_priority": pref.is_low_priority}
    )
