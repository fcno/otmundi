import pytest
from django.db import IntegrityError

from apps.engine.killstats.models.creature_config import CreatureConfig
from apps.game_data.creatures.models import Creature


@pytest.mark.django_db
class TestCreatureConfig:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.creature = Creature.objects.create(name="Orshabaal")
        self.config = CreatureConfig.objects.create(
            creature=self.creature, is_active=True
        )

    def test_create_config_with_null_intervals(self) -> None:
        """Valida que o sistema aceita intervalos nulos (Cenário Cold Start)."""

        assert self.config.creature == self.creature
        assert self.config.min_interval is None
        assert self.config.max_interval is None

    def test_one_to_one_constraint(self) -> None:
        """Garante que não é possível criar dois metadados para a mesma criatura."""
        with pytest.raises(IntegrityError):
            CreatureConfig.objects.create(creature=self.creature)

    def test_str_representation_with_values(self) -> None:
        """Testa a string formatada incluindo o status Active."""
        self.config.min_interval = 5
        self.config.max_interval = 15
        res = str(self.config)
        assert "Active" in res
        assert "Config: orshabaal" in res
        assert "(5-15" in res

    def test_str_representation_with_nulls(self) -> None:
        """Testa se a representação exibe '?' quando os dados são nulos."""
        config = CreatureConfig(creature=self.creature)
        res = str(config)
        assert "?" in res
        assert "(?-?" in res

    def test_cascade_on_creature_delete(self) -> None:
        """Garante que se a criatura sumir, o metadado some junto."""
        assert CreatureConfig.objects.count() == 1
        self.creature.delete()
        assert CreatureConfig.objects.count() == 0

    def test_model_validation_zero_value(self) -> None:
        """Garante que a model valida o valor mínimo de 1 no full_clean."""
        from django.core.exceptions import ValidationError

        config = CreatureConfig(creature=self.creature, min_interval=0)

        # O Django não valida no .save() por padrão, precisamos chamar o full_clean
        with pytest.raises(ValidationError) as excinfo:
            config.full_clean()
        assert "min_interval" in excinfo.value.message_dict

    def test_is_active_initial_state(self) -> None:
        """Garante que novas criaturas com config desativada não são 'active' por padrão."""
        m2 = Creature.objects.create(name="Rat")
        cfg2 = CreatureConfig.objects.create(creature=m2, is_active=False)
        assert cfg2.is_active is False
