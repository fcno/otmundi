from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import ListView

from apps.engine.killstats.forms.creature_config_form import CreatureConfigForm
from apps.engine.killstats.models.creature_config import CreatureConfig
from apps.engine.killstats.services.creature_event_service import CreatureEventService
from apps.game_data.creatures.models import Creature

if TYPE_CHECKING:
    CuratorBaseView = ListView[Creature]
else:
    CuratorBaseView = ListView


class CreatureCuratorView(PermissionRequiredMixin, CuratorBaseView):
    """
    View para gestão e validação manual das janelas de spawn.
    """

    model = Creature
    template_name = "curator.html"
    context_object_name = "creature"
    permission_required = "killstats.change_creatureconfig"

    def get_queryset(self) -> QuerySet[Creature]:
        """
        Retorna apenas criaturas ativas, consistente com o Monitor.
        """
        return Creature.objects.filter(config__is_active=True).select_related("config")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Injeta as sugestões calculadas pelo service em cada criatura
        for creature in context["creature"]:
            creature.suggestion = CreatureEventService.get_suggested_window(creature.id)

        return context

    def post(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """
        Processa a submissão manual dos intervalos de spawn.
        """
        creature_id = request.POST.get("creature_id")
        instance = CreatureConfig.objects.filter(creature_id=creature_id).first()

        form = CreatureConfigForm(request.POST, instance=instance)

        if form.is_valid():
            config = form.save(commit=False)
            config.creature_id = creature_id
            config.validated_at = timezone.now()
            config.validated_by = request.user
            config.save()
            messages.success(request, _("Updated successfully."))
        else:
            # Pega apenas a primeira mensagem de erro para o alert do DaisyUI
            first_error = str(next(iter(form.errors.values()))[0])
            messages.error(request, first_error)

        return redirect("killstats:creature_curator")
