import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse

from apps.engine.killstats.models.monster_config import MonsterConfig
from apps.game_data.monsters.models import Monster

User = get_user_model()


@pytest.mark.django_db
class TestBossCuratorView:
    @pytest.fixture(autouse=True)
    def setup(self, client: Client) -> None:
        self.client = client
        self.user = User.objects.create_user(username="curator_boss", password="123")
        self.monster = Monster.objects.create(name="ghazbaran")
        # Config inicial ativa
        self.config = MonsterConfig.objects.create(monster=self.monster, is_active=True)
        self.url = reverse("killstats:boss_curator")

    def test_curator_access_denied_without_permission(self) -> None:
        """403 para usuários sem a permissão killstats.change_monsterconfig."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert response.status_code == 403

    def test_curator_post_success_and_audit_fields(self) -> None:
        """Valida se o POST salva corretamente e registra QUEM e QUANDO."""
        perm = Permission.objects.get(codename="change_monsterconfig")
        self.user.user_permissions.add(perm)
        self.client.force_login(self.user)

        payload = {"monster_id": self.monster.id, "min_interval": 2, "max_interval": 4, "is_active": False }
        response = self.client.post(self.url, payload)

        assert response.status_code == 302
        config = MonsterConfig.objects.get(monster=self.monster)
        assert config.min_interval == 2
        assert config.max_interval == 4
        assert config.validated_by == self.user
        assert config.validated_at is not None
        assert config.is_active is False

    def test_curator_post_error_message_display(self) -> None:
        """Valida que a mensagem de erro do formulário é repassada para o context do Django."""
        perm = Permission.objects.get(codename="change_monsterconfig")
        self.user.user_permissions.add(perm)
        self.client.force_login(self.user)

        # Envio de Min > Max
        payload = {"monster_id": self.monster.id, "min_interval": 10, "max_interval": 2}
        response = self.client.post(self.url, payload, follow=True)

        messages = list(response.context["messages"])
        assert len(messages) > 0
        # Aqui garantimos que o erro "Minimum interval cannot..." chegou na View
        assert "Minimum interval" in str(messages[0])
