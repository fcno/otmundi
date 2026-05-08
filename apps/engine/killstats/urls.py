from django.urls import path

from .views.boss_curator import BossCuratorView
from .views.killstat_monitor import KillstatMonitorView

app_name = "killstats"

urlpatterns = [
    path("monitor/", KillstatMonitorView.as_view(), name="boss_monitor"),
    path("curator/", BossCuratorView.as_view(), name="boss_curator"),
]
