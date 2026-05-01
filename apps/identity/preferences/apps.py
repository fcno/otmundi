from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PreferencesConfig(AppConfig):
    name = "apps.identity.preferences"
    verbose_name = _("Preferences")
