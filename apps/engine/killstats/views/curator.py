from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import ListView

from apps.engine.killstats.forms.monster_metadata_form import MonsterMetadataForm
from apps.engine.killstats.models.monster_metadata import MonsterMetadata
from apps.engine.killstats.services.monster_event_service import MonsterEventService
from apps.game_data.monsters.models.monster import Monster

if TYPE_CHECKING:
    CuratorBaseView = ListView[Monster]
else:
    CuratorBaseView = ListView


class BossCuratorView(PermissionRequiredMixin, CuratorBaseView):
    """
    View para gestão e validação manual das janelas de spawn.
    """

    model = Monster
    template_name = "curator.html"
    context_object_name = "bosses"
    permission_required = "killstats.change_monstermetadata"

    def get_queryset(self) -> QuerySet[Monster]:
        """
        Retorna apenas bosses ativos, consistente com o Monitor.
        """
        return Monster.objects.filter(is_active=True).prefetch_related("metadata")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Injeta as sugestões calculadas pelo service em cada boss
        for boss in context["bosses"]:
            boss.suggestion = MonsterEventService.get_suggested_window(boss.id)

        return context

    def post(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """
        Processa a submissão manual dos intervalos de spawn.
        """
        monster_id = request.POST.get("monster_id")
        instance = MonsterMetadata.objects.filter(monster_id=monster_id).first()

        form = MonsterMetadataForm(request.POST, instance=instance)

        if form.is_valid():
            metadata = form.save(commit=False)
            metadata.monster_id = monster_id
            metadata.validated_at = timezone.now()
            metadata.validated_by = request.user
            metadata.save()
            messages.success(request, _("Updated successfully."))
        else:
            # Pega apenas a primeira mensagem de erro para o alert do DaisyUI
            first_error = str(next(iter(form.errors.values()))[0])
            messages.error(request, first_error)

        return redirect("killstats:boss_curator")
