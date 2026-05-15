from datetime import timedelta

import pytest
from django.utils import timezone

from apps.engine.killstats.models.creature_config import CreatureConfig
from apps.engine.killstats.models.creature_spawn_event import CreatureSpawnEvent
from apps.game_data.creatures.models import Creature
from apps.game_data.worlds.models.world import World


@pytest.mark.django_db
class TestKillstatsSignals:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.creature = Creature.objects.create(name="gaz'haragoth")
        CreatureConfig.objects.create(creature=self.creature, is_active=True)
        self.world = World.objects.create(name="ferobra")
        self.now = timezone.now()

    def test_automatic_config_update_on_event_creation(self) -> None:
        """
        Garante que a criação de um evento dispara o aprendizado via Signal
        sem intervenção manual.
        """
        # Evento 1: Há 20 dias
        CreatureSpawnEvent.objects.create(
            creature=self.creature,
            world=self.world,
            timestamp=self.now - timedelta(days=20),
        )
        # Evento 2: Hoje (Gatilho)
        CreatureSpawnEvent.objects.create(
            creature=self.creature, world=self.world, timestamp=self.now
        )

        # Verificamos se o Config foi criado e atualizado "sozinho"
        config = CreatureConfig.objects.get(creature=self.creature)
        assert config.min_interval == 20
        assert config.max_interval == 20

    def test_signal_does_not_recalibrate_on_update(self) -> None:
        """
        Caso de Borda: Edições em eventos existentes NÃO devem disparar nova calibração.
        O aprendizado deve ser baseado em NOVOS fatos (created=True).
        """
        # Criamos o cenário inicial
        event = CreatureSpawnEvent.objects.create(
            creature=self.creature,
            world=self.world,
            timestamp=self.now - timedelta(days=10),
        )
        CreatureSpawnEvent.objects.create(
            creature=self.creature, world=self.world, timestamp=self.now
        )

        # Forçamos um valor inicial no config
        config = CreatureConfig.objects.get(creature=self.creature)
        config.min_interval = 10
        config.save()

        # Editamos o evento (ex: mudando quem reportou ou flag is_puff)
        event.is_puff = True
        event.save()  # Isso dispara o post_save com created=False

        # Verificamos que o config permanece o mesmo (não houve recalibração desnecessária)
        config.refresh_from_db()
        assert config.min_interval == 10

    def test_signal_with_multiple_creatures_isolation(self) -> None:
        """
        Garante que o evento de uma criatura não afeta o metadado de outra.
        """
        # 1. Criamos outra criatura com uma configuração específica
        other_creature = Creature.objects.create(name="morgaroth")
        other_config = CreatureConfig.objects.create(
            creature=other_creature,
            is_active=True,
            min_interval=10,  # Valor para controle
            max_interval=20,
        )

        # 2. Criamos um evento para a criatura original (self.creature)
        # Isso disparará sinais que poderiam tentar recalcular intervalos
        CreatureSpawnEvent.objects.create(
            creature=self.creature, world=self.world, timestamp=self.now
        )

        # 3. Verificamos se a config da outra criatura continua EXATAMENTE igual
        other_config.refresh_from_db()
        assert other_config.min_interval == 10
        assert other_config.max_interval == 20
        assert other_config.is_active is True
        assert other_config.creature.name == "morgaroth"

    def test_signal_learning_with_puff_events(self) -> None:
        """
        Garante que eventos do tipo 'Puff' são tratados como resets válidos
        para o aprendizado de intervalos.
        """
        # Evento 1: Um Puff há 11 dias
        CreatureSpawnEvent.objects.create(
            creature=self.creature,
            world=self.world,
            timestamp=self.now - timedelta(days=11),
            is_puff=True,
        )

        # Evento 2: Uma Morte (Kill) hoje
        # O intervalo de 11 dias deve ser computado.
        CreatureSpawnEvent.objects.create(
            creature=self.creature, world=self.world, timestamp=self.now, is_puff=False
        )

        config = CreatureConfig.objects.get(creature=self.creature)
        assert config.min_interval == 11
