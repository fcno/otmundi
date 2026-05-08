from django.urls import path

from .views.curator import BossCuratorView
from .views.monitor import BossMonitorView

app_name = "killstats"

urlpatterns = [
    path("monitor/", BossMonitorView.as_view(), name="boss_monitor"),
    path("curator/", BossCuratorView.as_view(), name="boss_curator"),
]
