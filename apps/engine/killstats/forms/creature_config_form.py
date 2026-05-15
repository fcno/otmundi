from typing import TYPE_CHECKING, Any

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.engine.killstats.models.creature_config import CreatureConfig

# Se estivermos apenas checando tipos, o Mypy vê o Generic.
# Em execução, o Python ignora.
if TYPE_CHECKING:
    BaseForm = forms.ModelForm[CreatureConfig]
else:
    BaseForm = forms.ModelForm


class CreatureConfigForm(BaseForm):
    class Meta:
        model = CreatureConfig
        fields = ["is_active", "min_interval", "max_interval"]

    def clean(self) -> dict[str, Any]:
        """
        Valida a integridade lógica dos intervalos.
        """
        cleaned_data = super().clean()
        if not cleaned_data:
            return {}
        min_val = cleaned_data.get("min_interval")
        max_val = cleaned_data.get("max_interval")

        # Validamos apenas a relação entre os campos.
        # A validação de "maior que zero" o Django já fez no super().clean()
        # devido ao MinValueValidator(1) que colocamos na Model.
        if min_val is not None and max_val is not None:
            if min_val > max_val:
                self.add_error(
                    "min_interval",
                    _("Minimum interval cannot be greater than maximum."),
                )

        return cleaned_data
