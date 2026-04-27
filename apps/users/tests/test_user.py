import pytest
from django.db.utils import IntegrityError

from apps.users.models import User


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_with_email_success(self) -> None:
        """Testa a criação de um usuário comum com sucesso."""
        user = User.objects.create_user(
            username="testuser", email="test@otmundi.com", password="password123"
        )
        assert user.username == "testuser"
        assert user.email == "test@otmundi.com"
        assert user.is_active
        assert not user.is_staff

    def test_create_superuser_success(self) -> None:
        """Testa a criação de um superusuário (admin)."""
        admin = User.objects.create_superuser(
            username="admin", email="admin@otmundi.com", password="adminpassword"
        )
        assert admin.is_staff
        assert admin.is_superuser

    def test_duplicate_username_raises_error(self) -> None:
        """Edge case: Garante que não existam dois usuários com o mesmo username."""
        User.objects.create_user(username="unique", email="1@test.com", password="p")
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username="unique", email="2@test.com", password="p"
            )

    def test_duplicate_email_raises_error(self) -> None:
        """Edge case: O email deve ser único conforme nossa definição no modelo."""
        User.objects.create_user(username="user1", email="same@test.com", password="p")
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username="user2", email="same@test.com", password="p"
            )

    def test_str_representation(self) -> None:
        """Testa se a representação em string retorna o username."""
        user = User(username="tibia_player")
        assert str(user) == "tibia_player"
