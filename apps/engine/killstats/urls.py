from django.urls import path

from apps.engine.killstats.views.creature_curator import CreatureCuratorView
from apps.engine.killstats.views.creature_spawn_event_report import (
    CreatureSpawnEventCreateView,
)
from apps.engine.killstats.views.killstat_monitor import KillstatMonitorView
from apps.engine.killstats.views.preference_actions import toggle_creature_preference

app_name = "killstats"

urlpatterns = [
    path("monitor/", KillstatMonitorView.as_view(), name="creature_monitor"),
    path("curator/", CreatureCuratorView.as_view(), name="creature_curator"),
    path("report-spawn/", CreatureSpawnEventCreateView.as_view(), name="report_spawn"),
    path("toggle-preference/", toggle_creature_preference, name="toggle_preference"),
]
