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

    def test_preference_creation_and_fields(self) -> None:
        """Testa a criação com campos específicos e o timestamp de atualização."""
        # Comentário: Campos atualizados para is_low_priority e is_pinned[cite: 7, 10]
        pref = UserMonsterPreference.objects.create(
            user=self.user, monster=self.monster, is_low_priority=True, is_pinned=True
        )
        assert pref.is_low_priority is True
        assert pref.is_pinned is True
        assert pref.updated_at is not None

    def test_unique_constraint_user_monster(self) -> None:
        """Caso de borda: Impede que o mesmo usuário tenha duas preferências para o mesmo monstro."""
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
        """Testa o retorno do método __str__."""
        pref = UserMonsterPreference(user=self.user, monster=self.monster)
        assert "player_test" in str(pref)
        assert "ferumbras" in str(pref)  # Lowercase devido ao save() do Monster

    def test_cascade_on_user_delete(self) -> None:
        """Caso de borda: Preferências devem ser removidas se o usuário for deletado."""
        UserMonsterPreference.objects.create(user=self.user, monster=self.monster)
        self.user.delete()
        assert UserMonsterPreference.objects.count() == 0
