import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from apps.monsters.models.monster import Monster
from apps.preferences.models.user_monster_preference import UserMonsterPreference

User = get_user_model()


@pytest.mark.django_db
class TestUserMonsterPreference:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user = User.objects.create_user(username="player_test", password="pw")
        self.monster = Monster.objects.create(name="Ferumbras", is_active=True)

    def test_preference_custom_values(self) -> None:
        """Testa a criação com campos específicos e o timestamp de atualização."""
        # Comentário: Campos atualizados para is_low_priority e is_pinned
        pref = UserMonsterPreference.objects.create(
            user=self.user, monster=self.monster, is_low_priority=True, is_pinned=True
        )
        assert pref.is_low_priority is True
        assert pref.is_pinned is True
        assert pref.updated_at is not None

    def test_preference_creation_and_default_fields(self) -> None:
        """Testa criação e garante que os campos iniciam desativados por padrão."""
        pref = UserMonsterPreference.objects.create(
            user=self.user, monster=self.monster
        )
        assert pref.is_pinned is False
        assert pref.is_low_priority is False
        assert pref.updated_at is not None

    def test_unique_constraint_user_monster(self) -> None:
        """Caso de borda: Impede duplicidade de preferência para o mesmo par usuário/monstro."""
        UserMonsterPreference.objects.create(user=self.user, monster=self.monster)
        with pytest.raises(IntegrityError):
            UserMonsterPreference.objects.create(user=self.user, monster=self.monster)

    def test_multiple_monsters_same_user(self) -> None:
        """Garante que um usuário pode ter preferências para monstros diferentes."""
        monster2 = Monster.objects.create(name="Morgaroth", is_active=True)
        UserMonsterPreference.objects.create(user=self.user, monster=self.monster)
        UserMonsterPreference.objects.create(user=self.user, monster=monster2)
        assert UserMonsterPreference.objects.filter(user=self.user).count() == 2

    def test_str_representation(self) -> None:
        """Testa o retorno amigável do método __str__."""
        pref = UserMonsterPreference(user=self.user, monster=self.monster)
        assert self.user.username in str(pref)
        assert self.monster.name.lower() in str(pref).lower()

    def test_cascade_on_user_delete(self) -> None:
        """Caso de borda: Garante a limpeza das preferências ao deletar o usuário."""
        UserMonsterPreference.objects.create(user=self.user, monster=self.monster)
        self.user.delete()
        assert UserMonsterPreference.objects.count() == 0
