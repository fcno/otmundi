import pytest
from django.db import IntegrityError

from apps.monsters.models.monster import Monster
from apps.monsters.models.monster_metadata import MonsterMetadata


@pytest.mark.django_db
class TestMonsterMetadata:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.monster = Monster.objects.create(name="Orshabaal", is_active=True)

    def test_create_metadata_with_null_intervals(self) -> None:
        """Valida que o sistema aceita intervalos nulos (Cenário Cold Start)."""
        metadata = MonsterMetadata.objects.create(monster=self.monster)

        assert metadata.monster == self.monster
        assert metadata.min_interval is None
        assert metadata.max_interval is None

    def test_one_to_one_constraint(self) -> None:
        """Garante que não é possível criar dois metadados para o mesmo monstro."""
        MonsterMetadata.objects.create(monster=self.monster)

        with pytest.raises(IntegrityError):
            MonsterMetadata.objects.create(monster=self.monster)

    def test_str_representation_with_values(self) -> None:
        """Testa a string formatada com valores preenchidos."""
        metadata = MonsterMetadata(
            monster=self.monster, min_interval=5, max_interval=15
        )
        res = str(metadata)
        assert "Config: orshabaal" in res
        assert "(5-15" in res

    def test_str_representation_with_nulls(self) -> None:
        """Testa se a representação exibe '?' quando os dados são nulos."""
        metadata = MonsterMetadata(monster=self.monster)
        res = str(metadata)
        assert "?" in res
        assert "(?-?" in res

    def test_cascade_on_monster_delete(self) -> None:
        """Garante que se o monstro sumir, o metadado some junto."""
        MonsterMetadata.objects.create(monster=self.monster)
        self.monster.delete()
        assert MonsterMetadata.objects.count() == 0
