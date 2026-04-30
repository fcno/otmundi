from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.killstats.services.prediction_service import PredictionStatus
from apps.monsters.models.monster import Monster
from apps.monsters.models.monster_metadata import MonsterMetadata
from apps.worlds.models.world import World


@pytest.mark.django_db
class TestBossMonitorView:
    def test_view_lists_all_monsters_regardless_of_metadata(
        self, client: Client
    ) -> None:
        """Valida que a view exibe todos os monstros, mesmo sem metadados."""
        World.objects.create(name="antica")
        Monster.objects.create(name="orshabaal")
        Monster.objects.create(name="rat")

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
        Monster.objects.create(name="orshabaal")

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
        5. Collecting (Peso 3) - Ordem Alfabética (A)
        6. Collecting (Peso 3) - Ordem Alfabética (B)
        7. Missing (Peso 4)
        """
        world = World.objects.create(name="antica")
        now = timezone.now()

        # Criando os dados para forçar cada status
        # 1. Overdue
        m1 = Monster.objects.create(name="overdue_boss")
        MonsterMetadata.objects.create(monster=m1, min_interval=5, max_interval=10)
        MonsterSpawnEvent.objects.create(
            monster=m1, world=world, timestamp=now - timedelta(days=11)
        )

        # 2. Expected High (100%)
        m2 = Monster.objects.create(name="expected_high")
        MonsterMetadata.objects.create(monster=m2, min_interval=5, max_interval=10)
        MonsterSpawnEvent.objects.create(
            monster=m2, world=world, timestamp=now - timedelta(days=10)
        )

        # 3. Expected Low (50%)
        m3 = Monster.objects.create(name="expected_low")
        MonsterMetadata.objects.create(monster=m3, min_interval=10, max_interval=20)
        MonsterSpawnEvent.objects.create(
            monster=m3, world=world, timestamp=now - timedelta(days=15)
        )

        # 4. No Chance
        m4 = Monster.objects.create(name="no_chance_boss")
        MonsterMetadata.objects.create(monster=m4, min_interval=10, max_interval=20)
        MonsterSpawnEvent.objects.create(
            monster=m4, world=world, timestamp=now - timedelta(days=2)
        )

        # 5 e 6. Collecting (Empate por nome)
        Monster.objects.create(name="b_collecting")
        Monster.objects.create(name="a_collecting")

        # 7. Missing
        m7 = Monster.objects.create(name="missing_boss")
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
        assert bosses[4].name == "a_collecting"  # Peso 3, Alfabético A
        assert bosses[5].name == "b_collecting"  # Peso 3, Alfabético B
        assert bosses[6].name == "missing_boss"  # Peso 4
