import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from apps.engine.killstats.models.monster_config import MonsterConfig
from apps.engine.killstats.models.user_preference import (
    UserKillStatPreference,
)
from apps.game_data.monsters.models import Monster

User = get_user_model()


@pytest.mark.django_db
class TestToggleMonsterPreferenceView:
    @pytest.fixture(autouse=True)
    def setup(self, client: Client) -> None:
        self.client = client
        self.user = User.objects.create_user(username="test_user", password="123")
        self.monster = Monster.objects.create(name="ghazbaran")
        MonsterConfig.objects.create(monster=self.monster, is_active=True)
        self.url = reverse("killstats:toggle_preference")

    def test_toggle_requires_login(self) -> None:
        """Garante que usuários anônimos não podem alterar preferências."""
        response = self.client.post(
            self.url, {"monster_id": self.monster.id, "action": "pin"}
        )
        assert response.status_code == 302  # Redirect para login

    def test_toggle_only_allows_post(self) -> None:
        """Garante que o método GET é proibido (require_POST)."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        assert response.status_code == 405

    def test_toggle_pin_mutual_exclusion(self) -> None:
        """Testa se ativar PIN desativa LOW_PRIORITY automaticamente."""
        self.client.force_login(self.user)
        # Estado inicial: Low Priority
        pref = UserKillStatPreference.objects.create(
            user=self.user, monster=self.monster, is_low_priority=True
        )

        self.client.post(self.url, {"monster_id": self.monster.id, "action": "pin"})
        pref.refresh_from_db()

        assert pref.is_pinned is True
        assert pref.is_low_priority is False

    def test_toggle_low_priority_mutual_exclusion(self) -> None:
        """Testa se ativar LOW_PRIORITY desativa PIN automaticamente."""
        self.client.force_login(self.user)
        pref = UserKillStatPreference.objects.create(
            user=self.user, monster=self.monster, is_pinned=True
        )

        self.client.post(
            self.url, {"monster_id": self.monster.id, "action": "low_priority"}
        )
        pref.refresh_from_db()

        assert pref.is_low_priority is True
        assert pref.is_pinned is False

    def test_toggle_invalid_monster_returns_404(self) -> None:
        """Valida comportamento com ID de monstro inexistente."""
        self.client.force_login(self.user)
        response = self.client.post(self.url, {"monster_id": 999, "action": "pin"})
        assert response.status_code == 404
