import pytest

from apps.engine.killstats.forms.monster_metadata_form import MonsterMetadataForm


@pytest.mark.django_db
class TestMonsterMetadataForm:
    def test_form_valid_data(self) -> None:
        """Dados válidos e borda (Min == Max)."""
        assert (
            MonsterMetadataForm(data={"min_interval": 5, "max_interval": 10}).is_valid()
            is True
        )
        assert (
            MonsterMetadataForm(data={"min_interval": 7, "max_interval": 7}).is_valid()
            is True
        )

    def test_form_invalid_logic_min_greater_than_max(self) -> None:
        """Erro: Min > Max deve invalidar o formulário e apontar o erro no campo min."""
        form = MonsterMetadataForm(data={"min_interval": 10, "max_interval": 5})
        assert form.is_valid() is False
        assert "min_interval" in form.errors
        assert (
            form.errors["min_interval"][0]
            == "Minimum interval cannot be greater than maximum."
        )

    def test_form_non_numeric_data(self) -> None:
        """Erro: Envio de strings ou caracteres especiais."""
        form = MonsterMetadataForm(data={"min_interval": "abc", "max_interval": 10})
        assert form.is_valid() is False
        assert "min_interval" in form.errors

        form = MonsterMetadataForm(data={"min_interval": 10, "max_interval": "abc"})
        assert form.is_valid() is False
        assert "max_interval" in form.errors
