import pytest
from django.db import IntegrityError

from apps.engine.killstats.models.monster_config import MonsterConfig
from apps.game_data.monsters.models.monster import Monster


@pytest.mark.django_db
class TestMonsterConfig:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.monster = Monster.objects.create(name="Orshabaal", is_active=True)

    def test_create_config_with_null_intervals(self) -> None:
        """Valida que o sistema aceita intervalos nulos (Cenário Cold Start)."""
        config = MonsterConfig.objects.create(monster=self.monster)

        assert config.monster == self.monster
        assert config.min_interval is None
        assert config.max_interval is None

    def test_one_to_one_constraint(self) -> None:
        """Garante que não é possível criar dois metadados para o mesmo monstro."""
        MonsterConfig.objects.create(monster=self.monster)

        with pytest.raises(IntegrityError):
            MonsterConfig.objects.create(monster=self.monster)

    def test_str_representation_with_values(self) -> None:
        """Testa a string formatada com valores preenchidos."""
        config = MonsterConfig(monster=self.monster, min_interval=5, max_interval=15)
        res = str(config)
        assert "Config: orshabaal" in res
        assert "(5-15" in res

    def test_str_representation_with_nulls(self) -> None:
        """Testa se a representação exibe '?' quando os dados são nulos."""
        config = MonsterConfig(monster=self.monster)
        res = str(config)
        assert "?" in res
        assert "(?-?" in res

    def test_cascade_on_monster_delete(self) -> None:
        """Garante que se o monstro sumir, o metadado some junto."""
        MonsterConfig.objects.create(monster=self.monster)
        self.monster.delete()
        assert MonsterConfig.objects.count() == 0

    def test_model_validation_zero_value(self) -> None:
        """Garante que a model valida o valor mínimo de 1 no full_clean."""
        from django.core.exceptions import ValidationError

        config = MonsterConfig(monster=self.monster, min_interval=0)

        # O Django não valida no .save() por padrão, precisamos chamar o full_clean
        with pytest.raises(ValidationError) as excinfo:
            config.full_clean()
        assert "min_interval" in excinfo.value.message_dict
