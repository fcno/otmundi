from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from apps.monsters.models.monster import Monster
from apps.preferences.models.user_monster_preference import UserMonsterPreference


@login_required
@require_POST
def toggle_monster_preference(request: HttpRequest) -> JsonResponse:
    """
    Alterna preferências de exibição com exclusão mútua condicional.
    """

    assert request.user.is_authenticated

    monster_id = request.POST.get("monster_id")
    action = request.POST.get("action")

    monster = get_object_or_404(Monster, id=monster_id)

    pref, _ = UserMonsterPreference.objects.get_or_create(
        user=request.user, monster=monster
    )

    if action == "pin":
        pref.is_pinned = not pref.is_pinned
        if pref.is_pinned:
            pref.is_low_priority = False

    elif action == "low_priority":
        pref.is_low_priority = not pref.is_low_priority
        if pref.is_low_priority:
            pref.is_pinned = False

    pref.save()

    return JsonResponse(
        {
            "status": "success",
            "is_pinned": pref.is_pinned,
            "is_low_priority": pref.is_low_priority,
        }
    )
