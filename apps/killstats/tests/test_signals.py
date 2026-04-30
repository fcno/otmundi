from datetime import timedelta

import pytest
from django.utils import timezone

from apps.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.monsters.models.monster import Monster
from apps.monsters.models.monster_metadata import MonsterMetadata
from apps.worlds.models.world import World


@pytest.mark.django_db
class TestKillstatsSignals:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.monster = Monster.objects.create(name="gaz'haragoth", is_active=True)
        self.world = World.objects.create(name="ferobra")
        self.now = timezone.now()

    def test_automatic_metadata_update_on_event_creation(self) -> None:
        """
        Garante que a criação de um evento dispara o aprendizado via Signal
        sem intervenção manual.
        """
        # Evento 1: Há 20 dias
        MonsterSpawnEvent.objects.create(
            monster=self.monster,
            world=self.world,
            timestamp=self.now - timedelta(days=20),
        )
        # Evento 2: Hoje (Gatilho)
        MonsterSpawnEvent.objects.create(
            monster=self.monster, world=self.world, timestamp=self.now
        )

        # Verificamos se o Metadata foi criado e atualizado "sozinho"
        metadata = MonsterMetadata.objects.get(monster=self.monster)
        assert metadata.min_interval == 20
        assert metadata.max_interval == 20

    def test_signal_does_not_recalibrate_on_update(self) -> None:
        """
        Caso de Borda: Edições em eventos existentes NÃO devem disparar nova calibração.
        O aprendizado deve ser baseado em NOVOS fatos (created=True).
        """
        # Criamos o cenário inicial
        event = MonsterSpawnEvent.objects.create(
            monster=self.monster,
            world=self.world,
            timestamp=self.now - timedelta(days=10),
        )
        MonsterSpawnEvent.objects.create(
            monster=self.monster, world=self.world, timestamp=self.now
        )

        # Forçamos um valor inicial no metadata
        metadata = MonsterMetadata.objects.get(monster=self.monster)
        metadata.min_interval = 10
        metadata.save()

        # Editamos o evento (ex: mudando quem reportou ou flag is_puff)
        event.is_puff = True
        event.save()  # Isso dispara o post_save com created=False

        # Verificamos que o metadata permanece o mesmo (não houve recalibração desnecessária)
        metadata.refresh_from_db()
        assert metadata.min_interval == 10

    def test_signal_with_multiple_monsters_isolation(self) -> None:
        """
        Garante que o evento de um monstro não afeta o metadado de outro.
        """
        other_monster = Monster.objects.create(name="morgaroth", is_active=True)

        # Criamos evento para o Gaz'haragoth
        MonsterSpawnEvent.objects.create(
            monster=self.monster, world=self.world, timestamp=self.now
        )

        # O metadado do Morgaroth não deve existir/ser afetado
        assert not MonsterMetadata.objects.filter(monster=other_monster).exists()

    def test_signal_learning_with_puff_events(self) -> None:
        """
        Garante que eventos do tipo 'Puff' são tratados como resets válidos
        para o aprendizado de intervalos.
        """
        # Evento 1: Um Puff há 11 dias
        MonsterSpawnEvent.objects.create(
            monster=self.monster,
            world=self.world,
            timestamp=self.now - timedelta(days=11),
            is_puff=True,
        )

        # Evento 2: Uma Morte (Kill) hoje
        # O intervalo de 11 dias deve ser computado.
        MonsterSpawnEvent.objects.create(
            monster=self.monster, world=self.world, timestamp=self.now, is_puff=False
        )

        metadata = MonsterMetadata.objects.get(monster=self.monster)
        assert metadata.min_interval == 11
