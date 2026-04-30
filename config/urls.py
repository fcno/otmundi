from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("killstats/", include("apps.killstats.urls")),
    path("preferences/", include("apps.preferences.urls")),
    # Suporte ao Tailwind Hot Reload
    path("__reload__/", include("django_browser_reload.urls")),
]
