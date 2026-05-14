from django.urls import path

from apps.engine.killstats.views.boss_curator import BossCuratorView
from apps.engine.killstats.views.killstat_monitor import KillstatMonitorView
from apps.engine.killstats.views.monster_spawn_event_report import (
    MonsterSpawnEventCreateView,
)
from apps.engine.killstats.views.preference_actions import toggle_monster_preference

app_name = "killstats"

urlpatterns = [
    path("monitor/", KillstatMonitorView.as_view(), name="boss_monitor"),
    path("curator/", BossCuratorView.as_view(), name="boss_curator"),
    path("report-spawn/", MonsterSpawnEventCreateView.as_view(), name="report_spawn"),
    path("toggle-preference/", toggle_monster_preference, name="toggle_preference"),
]
