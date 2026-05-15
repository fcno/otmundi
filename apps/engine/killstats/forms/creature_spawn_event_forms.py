from typing import TYPE_CHECKING, Any

from django import forms

from apps.engine.killstats.models.creature_spawn_event import CreatureSpawnEvent

if TYPE_CHECKING:
    EventFormBase = forms.ModelForm[CreatureSpawnEvent]
else:
    EventFormBase = forms.ModelForm


class CreatureSpawnEventForm(EventFormBase):
    class Meta:
        model = CreatureSpawnEvent
        fields = ["creature", "world", "timestamp", "is_puff"]
        widgets = {
            "timestamp": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "input input-bordered w-full"}
            ),
            "creature": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "world": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "is_puff": forms.CheckboxInput(
                attrs={"class": "checkbox checkbox-primary"}
            ),
        }

    def clean(self) -> dict[str, Any]:
        # A validação da UniqueConstraint (per dia) é feita automaticamente pelo Django no super().clean().
        cleaned_data = super().clean()

        if cleaned_data is None:
            return {}

        return cleaned_data
