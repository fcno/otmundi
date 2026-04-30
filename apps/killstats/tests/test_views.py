import pytest
from django.test import Client
from django.urls import reverse

from apps.killstats.services.prediction_service import PredictionStatus
from apps.monsters.models.monster import Monster
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
