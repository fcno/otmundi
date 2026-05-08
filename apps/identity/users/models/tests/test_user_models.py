import pytest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from apps.identity.users.models import User


@pytest.mark.django_db
class TestUserModel:
    # --- Testes de Criação e Identidade ---

    def test_create_user_with_email_success(self) -> None:
        """Testa a criação de um usuário comum com sucesso."""
        user = User.objects.create_user(
            username="testuser", email="test@otmundi.com", password="password123"
        )
        assert user.username == "testuser"
        assert user.email == "test@otmundi.com"
        assert user.is_active
        assert not user.is_staff
        assert user.role == User.Role.PLAYER

    def test_create_superuser_success(self) -> None:
        """Testa a criação de um superusuário (admin)."""
        admin = User.objects.create_superuser(
            username="admin", email="admin@otmundi.com", password="adminpassword"
        )
        assert admin.is_staff
        assert admin.is_superuser

    def test_str_representation(self) -> None:
        """Garante que o __str__ segue o padrão: username (Role)."""
        user = User(username="tibia_player", role=User.Role.PLAYER)
        assert str(user) == "tibia_player (Player)"

    # --- Testes de Restrições (Bordas) ---

    def test_duplicate_username_raises_error(self) -> None:
        """Edge case: Garante que não existam dois usuários com o mesmo username."""
        User.objects.create_user(username="unique", email="1@test.com", password="p")
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username="unique", email="2@test.com", password="p"
            )

    def test_duplicate_email_raises_error(self) -> None:
        """Edge case: O email deve ser único conforme definição no modelo."""
        User.objects.create_user(username="user1", email="same@test.com", password="p")
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username="user2", email="same@test.com", password="p"
            )

    # --- Testes de Hierarquia e Roles ---

    def test_role_hierarchy_values(self) -> None:
        """Valida a escala de 10 em 10 para futura expansão (Mypy safe)."""
        assert User.Role.PLAYER.value == 10
        assert User.Role.TUTOR.value == 20
        assert User.Role.SENIOR_TUTOR.value == 30
        assert User.Role.GAMEMASTER.value == 40
        assert User.Role.COMMUNITY_MANAGER.value == 50
        assert User.Role.ADMIN.value == 60

    def test_role_hierarchy_logic(self) -> None:
        """
        Garante que a precedência numérica respeita a ordem de autoridade.
        Essencial para ordenação em listagens e filtros de staff.
        """
        # Ordem decrescente de autoridade
        assert User.Role.ADMIN > User.Role.COMMUNITY_MANAGER
        assert User.Role.COMMUNITY_MANAGER > User.Role.GAMEMASTER
        assert User.Role.GAMEMASTER > User.Role.SENIOR_TUTOR
        assert User.Role.SENIOR_TUTOR > User.Role.TUTOR
        assert User.Role.TUTOR > User.Role.PLAYER

    def test_set_all_available_roles(self) -> None:
        """Cenários: Valida a atribuição de cada cargo da hierarquia."""
        roles = [
            (User.Role.TUTOR, "Tutor"),
            (User.Role.SENIOR_TUTOR, "Senior Tutor"),
            (User.Role.GAMEMASTER, "GameMaster"),
            (User.Role.COMMUNITY_MANAGER, "Community Manager"),
            (User.Role.ADMIN, "Administrator"),
        ]
        for role_value, display_name in roles:
            user = User.objects.create_user(
                username=f"user_{role_value}",
                email=f"e_{role_value}@test.com",
                role=role_value,
            )
            assert user.role == role_value
            assert user.get_role_display() == display_name

    def test_role_persistence_after_save(self) -> None:
        """Borda: Garante que a Role não se perde após updates no perfil."""
        user = User.objects.create_user(username="staff", role=User.Role.GAMEMASTER)
        user.first_name = "NovoNome"
        user.save()
        user.refresh_from_db()
        assert user.first_name == "NovoNome"
        assert user.role == User.Role.GAMEMASTER

    def test_invalid_role_raises_error_on_clean(self) -> None:
        """Borda: Garante que o Django rejeita valores fora das choices no clean."""
        user = User(username="hacker", email="h@test.com", role=99)
        with pytest.raises(ValidationError) as excinfo:
            user.full_clean()
        assert "role" in excinfo.value.message_dict

    # --- Testes de Permissões Dinâmicas (Banco de Dados) ---

    def test_role_permissions_via_database(self) -> None:
        """
        Cenário: Define permissões no banco para uma Role e verifica
        se o usuário a recebe via Grupo.
        """
        # Configuração de permissão de monitoramento (ex: killstats)
        content_type = ContentType.objects.get_for_model(User)
        perm = Permission.objects.create(
            codename="view_killstats",
            name="Can View Killstats",
            content_type=content_type,
        )

        # O grupo é criado automaticamente no save() do usuário, mas podemos garantir aqui
        group, _ = Group.objects.get_or_create(name="Tutor")
        group.permissions.add(perm)

        user = User.objects.create_user(username="tutor_monitor", role=User.Role.TUTOR)

        # Verificação
        assert user.groups.filter(name="Tutor").exists()
        assert user.has_perm("users.view_killstats") is True
