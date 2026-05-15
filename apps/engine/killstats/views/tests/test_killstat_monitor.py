from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.engine.killstats.models.creature_config import CreatureConfig
from apps.engine.killstats.models.creature_spawn_event import CreatureSpawnEvent
from apps.engine.killstats.models.user_preference import UserKillStatPreference
from apps.engine.killstats.services.prediction_service import PredictionStatus
from apps.game_data.creatures.models import Creature
from apps.game_data.worlds.models.world import World

User = get_user_model()


@pytest.mark.django_db
class TestCreatureMonitorView:

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup básico para garantir que o ambiente tenha um mundo e URL padrão."""
        self.world = World.objects.create(name="antica-monitor")
        self.url = reverse("killstats:creature_monitor")
        self.user = User.objects.create_user(username="monitor_user", password="pw")

    # --- Testes de Estado e Listagem ---

    def test_view_with_no_creatures_exists(self, client: Client) -> None:
        """Garante que a view renderiza sem erros mesmo se o banco estiver vazio."""
        response = client.get(self.url)
        assert response.status_code == 200
        assert len(response.context["creatures"]) == 0

    def test_view_logic_and_prediction_status(self, client: Client) -> None:
        """Valida filtragem básica e status inicial COLLECTING."""
        # Nomes únicos para evitar IntegrityError
        m1 = Creature.objects.create(name="orshabaal-status")
        CreatureConfig.objects.create(creature=m1, is_active=True)

        m2 = Creature.objects.create(name="rat-status")
        CreatureConfig.objects.create(creature=m2, is_active=False)

        response = client.get(self.url)
        creatures = response.context["creatures"]

        assert any(b.id == m1.id for b in creatures)
        assert not any(b.id == m2.id for b in creatures)

        for b in creatures:
            if b.id == m1.id:
                assert b.prediction["status_code"] == PredictionStatus.COLLECTING.value

    # --- Testes de Ordenação ---

    def test_view_sorting_with_user_preferences(self, client: Client) -> None:
        """Valida a hierarquia: Pinned > Status Weight > Chance > Name."""
        client.force_login(self.user)
        now = timezone.now()

        # Creature 1: Expected Soon (Weight 1) - Será PINNED
        b1 = Creature.objects.create(name="gazharagoth-sort")
        CreatureConfig.objects.create(
            creature=b1, is_active=True, min_interval=5, max_interval=10
        )
        CreatureSpawnEvent.objects.create(
            creature=b1, world=self.world, timestamp=now - timedelta(days=7)
        )

        # Creature 2: Overdue (Weight 0) - Naturalmente ficaria no topo, mas não é pinned
        b2 = Creature.objects.create(name="orshabaal-sort")
        CreatureConfig.objects.create(
            creature=b2, is_active=True, min_interval=5, max_interval=10
        )
        CreatureSpawnEvent.objects.create(
            creature=b2, world=self.world, timestamp=now - timedelta(days=12)
        )

        UserKillStatPreference.objects.create(
            user=self.user, creature=b1, is_pinned=True
        )

        response = client.get(self.url)
        creatures = list(response.context["creatures"])

        assert creatures[0].id == b1.id  # Pinned vence o Overdue
        assert creatures[1].id == b2.id

    def test_anonymous_user_sees_default_sorting(self, client: Client) -> None:
        """Garante que a ordenação padrão prioriza OVERDUE (0) sobre EXPECTED (1)."""
        now = timezone.now()

        # 1. CREATURE EXPECTED (Peso 1)
        # Morreu há 7 dias. Janela 5-10. Status: EXPECTED
        b_soon = Creature.objects.create(name="soon-creature")
        CreatureConfig.objects.create(
            creature=b_soon, is_active=True, min_interval=5, max_interval=10
        )
        CreatureSpawnEvent.objects.create(
            creature=b_soon, world=self.world, timestamp=now - timedelta(days=7)
        )

        # 2. CREATURE OVERDUE (Peso 0)
        # Morreu há 11 dias. Janela 5-10.
        # 11 dias está dentro da tolerância de 20% (10 * 1.2 = 12 dias).
        # Status: OVERDUE
        b_late = Creature.objects.create(name="late-creature")
        CreatureConfig.objects.create(
            creature=b_late, is_active=True, min_interval=5, max_interval=10
        )
        CreatureSpawnEvent.objects.create(
            creature=b_late, world=self.world, timestamp=now - timedelta(days=11)
        )

        response = client.get(self.url)
        creatures = list(response.context["creatures"])

        # Agora a ordenação deve colocar o OVERDUE (peso 0) no topo
        assert creatures[0].name == "late-creature"
        assert creatures[0].prediction["status_code"] == "OVERDUE"
        assert creatures[1].name == "soon-creature"
        assert creatures[1].prediction["status_code"] == "EXPECTED"

    # --- Testes de Toggles e Preferências ---

    def test_toggle_preference_pin_and_exclusion(self, client: Client) -> None:
        """Valida o PIN e a limpeza automática de Low Priority."""
        creature = Creature.objects.create(name="ghazbaran-toggle")
        CreatureConfig.objects.create(creature=creature, is_active=True)
        url_toggle = reverse("killstats:toggle_preference")

        client.force_login(self.user)
        pref = UserKillStatPreference.objects.create(
            user=self.user, creature=creature, is_low_priority=True
        )

        # Ativa o Pin via POST
        client.post(url_toggle, {"creature_id": creature.id, "action": "pin"})
        pref.refresh_from_db()

        assert pref.is_pinned is True
        assert pref.is_low_priority is False

    def test_toggle_action_unpin(self, client: Client) -> None:
        """Valida que o toggle de um PIN já existente o desativa."""
        creature = Creature.objects.create(name="ferumbras-unpin")
        CreatureConfig.objects.create(creature=creature, is_active=True)
        client.force_login(self.user)

        pref = UserKillStatPreference.objects.create(
            user=self.user, creature=creature, is_pinned=True
        )

        url_toggle = reverse("killstats:toggle_preference")
        client.post(url_toggle, {"creature_id": creature.id, "action": "pin"})
        pref.refresh_from_db()

        assert pref.is_pinned is False

    # --- Testes de Segurança e Contexto ---

    def test_view_prediction_disabled_no_world(self, client: Client) -> None:
        """Verifica comportamento quando não há mundos cadastrados."""
        World.objects.all().delete()
        response = client.get(self.url)
        assert response.status_code == 200
        assert response.context.get("prediction_enabled") is False

    def test_toggle_auth_required(self, client: Client) -> None:
        """Garante que toggle_preference exige login (redireciona)."""
        creature = Creature.objects.create(name="auth-check-creature")
        url = reverse("killstats:toggle_preference")
        resp = client.post(url, {"creature_id": creature.id, "action": "pin"})
        assert resp.status_code == 302

    def test_view_uses_correct_world_context(self, client: Client) -> None:
        """Garante que a predição reflete os eventos do mundo correto."""
        # 1. Setup de Mundos
        world_b = World.objects.create(
            name="belobra-context"
        )  # self.world já é Antica no setup

        # 2. Setup da Criatura (Nome único para evitar colisão)
        creature = Creature.objects.create(name="ghazbaran-context")
        CreatureConfig.objects.create(
            creature=creature, is_active=True, min_interval=5, max_interval=10
        )

        # 3. Criamos um evento APENAS no Mundo B (Belobra)
        # Se a view olhar para o Mundo A (Antica), o status deve ser COLLECTING
        # Se olhar para o Mundo B, deve ter predição baseada no tempo
        CreatureSpawnEvent.objects.create(
            creature=creature,
            world=world_b,
            timestamp=timezone.now() - timedelta(days=7),
        )

        # Acessando o monitor (assume o primeiro mundo ou o contexto padrão)
        # Se o seu sistema usa query params (?world=...), você pode testar a troca aqui
        response = client.get(self.url)
        creatures = response.context["creatures"]

        for b in creatures:
            if b.id == creature.id:
                # Como não há eventos no mundo padrão (Antica), deve ser COLLECTING
                assert b.prediction["status_code"] == PredictionStatus.COLLECTING.value
