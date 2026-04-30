from django.urls import path

from .views import toggle_monster_preference

app_name = "preferences"

urlpatterns = [
    path("toggle-preference/", toggle_monster_preference, name="toggle_preference"),
]
