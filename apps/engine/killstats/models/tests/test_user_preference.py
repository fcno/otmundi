import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from apps.engine.killstats.models.user_preference import (
    UserKillStatPreference,
)
from apps.game_data.monsters.models import Monster

User = get_user_model()


@pytest.mark.django_db
class TestUserKillStatPreference:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user = User.objects.create_user(username="player_test", password="pw")
        self.monster = Monster.objects.create(name="Ferumbras", is_active=True)

    def test_preference_custom_values(self) -> None:
        """Testa a criação com campos específicos e o timestamp de atualização."""
        # Comentário: Campos atualizados para is_low_priority e is_pinned
        pref = UserKillStatPreference.objects.create(
            user=self.user, monster=self.monster, is_low_priority=True, is_pinned=True
        )
        assert pref.is_low_priority is True
        assert pref.is_pinned is True
        assert pref.updated_at is not None

    def test_preference_creation_and_default_fields(self) -> None:
        """Testa criação e garante que os campos iniciam desativados por padrão."""
        pref = UserKillStatPreference.objects.create(
            user=self.user, monster=self.monster
        )
        assert pref.is_pinned is False
        assert pref.is_low_priority is False
        assert pref.updated_at is not None

    def test_unique_constraint_user_monster(self) -> None:
        """Caso de borda: Impede duplicidade de preferência para o mesmo par usuário/monstro."""
        UserKillStatPreference.objects.create(user=self.user, monster=self.monster)
        with pytest.raises(IntegrityError):
            UserKillStatPreference.objects.create(user=self.user, monster=self.monster)

    def test_multiple_monsters_same_user(self) -> None:
        """Garante que um usuário pode ter preferências para monstros diferentes."""
        monster2 = Monster.objects.create(name="Morgaroth", is_active=True)
        UserKillStatPreference.objects.create(user=self.user, monster=self.monster)
        UserKillStatPreference.objects.create(user=self.user, monster=monster2)
        assert UserKillStatPreference.objects.filter(user=self.user).count() == 2

    def test_str_representation(self) -> None:
        """Testa o retorno amigável do método __str__."""
        pref = UserKillStatPreference(user=self.user, monster=self.monster)
        assert self.user.username in str(pref)
        assert self.monster.name.lower() in str(pref).lower()

    def test_cascade_on_user_delete(self) -> None:
        """Caso de borda: Garante a limpeza das preferências ao deletar o usuário."""
        UserKillStatPreference.objects.create(user=self.user, monster=self.monster)
        self.user.delete()
        assert UserKillStatPreference.objects.count() == 0
