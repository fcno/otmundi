from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.killstats.services.prediction_service import PredictionStatus
from apps.monsters.models.monster import Monster
from apps.monsters.models.monster_metadata import MonsterMetadata
from apps.preferences.models.user_monster_preference import UserMonsterPreference
from apps.worlds.models.world import World

User = get_user_model()


@pytest.mark.django_db
class TestBossMonitorView:
    def test_view_lists_active_monsters_regardless_of_metadata(
        self, client: Client
    ) -> None:
        """Valida que a view exibe todos os monstros, mesmo sem metadados."""
        World.objects.create(name="antica")
        Monster.objects.create(name="orshabaal", is_active=True)
        Monster.objects.create(name="rat", is_active=True)

        url = reverse("killstats:boss_monitor")
        response = client.get(url)

        assert response.status_code == 200
        bosses = response.context["bosses"]
        assert len(bosses) == 2
        # Verifica se o monstro sem metadado assume o status COLLECTING
        rat = next(b for b in bosses if b.name == "rat")
        assert rat.prediction["status_code"] == PredictionStatus.COLLECTING.value

    def test_view_with_no_monsters_exists(self, client: Client) -> None:
        """Garante que a página carrega sem erros se o banco estiver vazio."""
        World.objects.create(name="antica")

        url = reverse("killstats:boss_monitor")
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.context["bosses"]) == 0

    def test_view_prediction_disabled_no_world(self, client: Client) -> None:
        """Testa o comportamento quando não há nenhum mundo cadastrado."""
        Monster.objects.create(name="orshabaal", is_active=True)

        url = reverse("killstats:boss_monitor")
        response = client.get(url)
        # A view deve definir prediction_enabled como False
        assert response.status_code == 200
        assert response.context["prediction_enabled"] is False

    def test_view_uses_correct_world_context(self, client: Client) -> None:
        """Garante que a view usa o primeiro mundo disponível para predições."""
        world_1 = World.objects.create(name="antica")
        World.objects.create(name="belobra")

        url = reverse("killstats:boss_monitor")
        response = client.get(url)

        assert response.context["current_world"] == world_1

    def test_view_sorting_all_statuses_and_ties(self, client: Client) -> None:
        """
        Cenário Completo:
        1. Overdue (Peso 0)
        2. Expected (Peso 1) - Maior chance primeiro
        3. Expected (Peso 1) - Menor chance depois
        4. No Chance (Peso 2)
        5. Missing (Peso 3)
        6. Collecting (Peso 4) - Ordem Alfabética (A)
        7. Collecting (Peso 4) - Ordem Alfabética (B)
        """
        world = World.objects.create(name="antica")
        now = timezone.now()

        # Criando os dados para forçar cada status
        # 1. Overdue
        m1 = Monster.objects.create(name="overdue_boss", is_active=True)
        MonsterMetadata.objects.create(monster=m1, min_interval=5, max_interval=10)
        MonsterSpawnEvent.objects.create(
            monster=m1, world=world, timestamp=now - timedelta(days=11)
        )

        # 2. Expected High (100%)
        m2 = Monster.objects.create(name="expected_high", is_active=True)
        MonsterMetadata.objects.create(monster=m2, min_interval=5, max_interval=10)
        MonsterSpawnEvent.objects.create(
            monster=m2, world=world, timestamp=now - timedelta(days=10)
        )

        # 3. Expected Low (50%)
        m3 = Monster.objects.create(name="expected_low", is_active=True)
        MonsterMetadata.objects.create(monster=m3, min_interval=10, max_interval=20)
        MonsterSpawnEvent.objects.create(
            monster=m3, world=world, timestamp=now - timedelta(days=15)
        )

        # 4. No Chance
        m4 = Monster.objects.create(name="no_chance_boss", is_active=True)
        MonsterMetadata.objects.create(monster=m4, min_interval=10, max_interval=20)
        MonsterSpawnEvent.objects.create(
            monster=m4, world=world, timestamp=now - timedelta(days=2)
        )

        # 5 e 6. Collecting (Empate por nome)
        Monster.objects.create(name="b_collecting", is_active=True)
        Monster.objects.create(name="a_collecting", is_active=True)

        # 7. Missing
        m7 = Monster.objects.create(name="missing_boss", is_active=True)
        MonsterMetadata.objects.create(monster=m7, min_interval=5, max_interval=10)
        MonsterSpawnEvent.objects.create(
            monster=m7, world=world, timestamp=now - timedelta(days=30)
        )

        url = reverse("killstats:boss_monitor")
        response = client.get(url)
        bosses = response.context["bosses"]

        # Verificação da Ordem Absoluta
        assert bosses[0].name == "overdue_boss"  # Peso 0
        assert bosses[1].name == "expected_high"  # Peso 1, Chance 100
        assert bosses[2].name == "expected_low"  # Peso 1, Chance 50
        assert bosses[3].name == "no_chance_boss"  # Peso 2
        assert bosses[4].name == "missing_boss"  # Peso 3
        assert bosses[5].name == "a_collecting"  # Peso 4, Alfabético A
        assert bosses[6].name == "b_collecting"  # Peso 4, Alfabético B

    def test_view_filters_inactive_monsters(self, client: Client) -> None:
        """Garante que monstros inativos não aparecem e não são processados."""
        World.objects.create(name="antica")

        # Setup: 1 Ativo e 2 Inativos
        Monster.objects.create(name="visible_boss", is_active=True)
        Monster.objects.create(name="hidden_boss_1", is_active=False)
        Monster.objects.create(name="hidden_boss_2", is_active=False)

        url = reverse("killstats:boss_monitor")
        response = client.get(url)

        bosses = response.context["bosses"]

        # 1. Validação de Quantidade: Apenas o ativo deve estar presente
        assert len(bosses) == 1
        assert bosses[0].name == "visible_boss"

        # 2. Validação Extrema: Garante que os inativos não existem no queryset
        active_names = [b.name for b in bosses]
        assert "hidden_boss_1" not in active_names
        assert "hidden_boss_2" not in active_names

    def test_view_ignores_inactive_monsters_but_keeps_data(
        self, client: Client
    ) -> None:
        """Valida que dados de monstros inativos existem no banco, mas são filtrados na View."""
        world = World.objects.create(name="antica")
        m1 = Monster.objects.create(name="silent_boss", is_active=False)

        # Cria evento para o monstro inativo
        MonsterSpawnEvent.objects.create(
            monster=m1, world=world, timestamp=timezone.now()
        )

        url = reverse("killstats:boss_monitor")
        response = client.get(url)

        # Na View não aparece nada
        assert len(response.context["bosses"]) == 0
        # No banco de dados o evento deve existir (Proposta 1)
        assert MonsterSpawnEvent.objects.filter(monster__name="silent_boss").exists()

    def test_view_sorting_with_user_preferences(self, client: Client) -> None:
        """
        Caso de borda extremo: Valida a hierarquia Pin > Status > Low Priority.
        1. 'rat' (Collecting - Peso 4) está PINNED -> Deve ir para o topo.
        2. 'orshabaal' (Overdue - Peso 0) é LOW PRIORITY -> Deve ir para o final.
        """
        world = World.objects.create(name="antica")
        user = User.objects.create_user(username="test_sorter", password="pw")
        client.force_login(user)

        # Criando monstro que seria o último (Collecting), mas será PINNED
        m_pin = Monster.objects.create(name="rat", is_active=True)
        UserMonsterPreference.objects.create(user=user, monster=m_pin, is_pinned=True)

        # Criando monstro que seria o primeiro (Overdue), mas será LOW PRIORITY
        m_low = Monster.objects.create(name="orshabaal", is_active=True)
        MonsterMetadata.objects.create(monster=m_low, min_interval=5, max_interval=10)
        MonsterSpawnEvent.objects.create(
            monster=m_low, world=world, timestamp=timezone.now() - timedelta(days=11)
        )
        UserMonsterPreference.objects.create(
            user=user, monster=m_low, is_low_priority=True
        )

        # Monstro normal (Expected - Peso 1) para ficar no meio
        m_norm = Monster.objects.create(name="normal_boss", is_active=True)
        MonsterMetadata.objects.create(monster=m_norm, min_interval=5, max_interval=10)
        MonsterSpawnEvent.objects.create(
            monster=m_norm, world=world, timestamp=timezone.now() - timedelta(days=7)
        )

        response = client.get(reverse("killstats:boss_monitor"))
        bosses = response.context["bosses"]

        # Verificação da nova hierarquia de visualização personalizada[cite: 8]
        assert bosses[0].name == "rat"  # Pinned ignora status peso 4
        assert bosses[1].name == "normal_boss"  # Ordem normal de status
        assert bosses[2].name == "orshabaal"  # Low Priority ignora status peso 0

    def test_anonymous_user_sees_default_sorting(self, client: Client) -> None:
        """Garante que as preferências de um usuário não afetam visitantes anônimos."""
        world = World.objects.create(name="antica")
        user = User.objects.create_user(username="other_user", password="pw")

        m_overdue = Monster.objects.create(name="overdue_boss", is_active=True)
        MonsterMetadata.objects.create(
            monster=m_overdue, min_interval=5, max_interval=10
        )
        MonsterSpawnEvent.objects.create(
            monster=m_overdue,
            world=world,
            timestamp=timezone.now() - timedelta(days=11),
        )
        # Este usuário prefere o overdue no final
        UserMonsterPreference.objects.create(
            user=user, monster=m_overdue, is_low_priority=True
        )

        # Visitante anônimo acessa a página
        response = client.get(reverse("killstats:boss_monitor"))
        bosses = response.context["bosses"]

        # Para o anônimo, a ordem deve ser a padrão de status (Overdue primeiro)[cite: 8]
        assert bosses[0].name == "overdue_boss"
