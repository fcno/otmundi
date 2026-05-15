import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.engine.killstats.models.creature_spawn_event import CreatureSpawnEvent
from apps.game_data.creatures.models.creature import Creature
from apps.game_data.worlds.models.world import World

User = get_user_model()


@pytest.mark.django_db
class TestCreatureSpawnEventCreateView:
    @pytest.fixture(autouse=True)
    def setup(self, client: Client) -> None:
        self.client = client
        self.user = User.objects.create_user(username="reporter", password="123")
        self.creature = Creature.objects.create(name="ghazbaran")
        self.world = World.objects.create(name="belobra")
        self.url = reverse("killstats:report_spawn")

    def test_report_access_denied_without_permission(self) -> None:
        """Acesso negado (302/403) para usuários sem permissão add_creaturespawnevent."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # Como usa PermissionRequiredMixin, o padrão é redirect para login ou 403
        assert response.status_code in [302, 403]

    def test_report_post_success_htmx(self) -> None:
        """Valida que o POST via HTMX salva o evento e injeta o reported_by."""
        perm = Permission.objects.get(codename="add_creaturespawnevent")
        self.user.user_permissions.add(perm)
        self.client.force_login(self.user)

        timestamp = timezone.now()
        payload = {
            "creature": self.creature.id,
            "world": self.world.id,
            "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M"),
            "is_puff": True,
        }

        # Simula requisição HTMX
        response = self.client.post(self.url, payload, HTTP_HX_REQUEST="true")

        assert response.status_code == 200
        # Verifica se o evento foi criado com o usuário correto
        event = CreatureSpawnEvent.objects.get(creature=self.creature)
        assert event.reported_by == self.user
        assert event.is_puff is True
        # Verifica se retornou o partial de sucesso
        assert "Event registered successfully!" in response.content.decode()

    def test_unique_constraint_violation_per_day(self) -> None:
        """Garante que dois eventos para a mesma criatura/dia/mundo falham (UniqueConstraint)."""
        perm = Permission.objects.get(codename="add_creaturespawnevent")
        self.user.user_permissions.add(perm)
        self.client.force_login(self.user)

        now = timezone.now()
        # Primeiro registro
        CreatureSpawnEvent.objects.create(
            creature=self.creature,
            world=self.world,
            timestamp=now,
            reported_by=self.user,
        )

        # Tentativa de segundo registro no mesmo dia
        payload = {
            "creature": self.creature.id,
            "world": self.world.id,
            "timestamp": now.strftime("%Y-%m-%dT%H:%M"),
        }

        response = self.client.post(self.url, payload, HTTP_HX_REQUEST="true")

        # O Django deve retornar erro de validação (422 na nossa view ou form errors no context)
        assert response.status_code == 422
        assert CreatureSpawnEvent.objects.count() == 1
