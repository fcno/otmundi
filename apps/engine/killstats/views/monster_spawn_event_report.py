from typing import TYPE_CHECKING, Any

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from apps.engine.killstats.forms.monster_spawn_event_forms import MonsterSpawnEventForm
from apps.engine.killstats.models.monster_spawn_event import MonsterSpawnEvent

if TYPE_CHECKING:
    EventCreateBase = CreateView[MonsterSpawnEvent, MonsterSpawnEventForm]
else:
    EventCreateBase = CreateView


class MonsterSpawnEventCreateView(PermissionRequiredMixin, EventCreateBase):
    model = MonsterSpawnEvent
    form_class = MonsterSpawnEventForm
    template_name = "killstats/report_spawn.html"
    permission_required = "killstats.add_monsterspawnevent"
    success_url = reverse_lazy("killstats:report_spawn")

    def form_valid(self, form: Any) -> HttpResponse:
        form.instance.reported_by = self.request.user

        if self.request.headers.get("HX-Request"):
            self.object = form.save()  # Salva a instância
            return render(
                self.request,
                "killstats/partials/event_form.html",
                {
                    "form": MonsterSpawnEventForm(),
                    "success_message": _("Event registered successfully!"),
                },
            )

        return super().form_valid(form)

    def form_invalid(self, form: Any) -> HttpResponse:
        if self.request.headers.get("HX-Request"):
            return render(
                self.request,
                "killstats/partials/event_form.html",
                {"form": form},
                status=422,
            )
        return super().form_invalid(form)
