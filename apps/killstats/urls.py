from django.urls import path
from .views import BossMonitorView

app_name = 'killstats'

urlpatterns = [
    path('monitor/', BossMonitorView.as_view(), name='boss_monitor'),
]
