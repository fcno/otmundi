from datetime import UTC, datetime

import pytest
from django.db import IntegrityError, transaction

from apps.engine.killstats.ingestion.dto import (
    CreatureStatsDTO,
    KillStatsMetricDTO,
    WorldKillStatsDTO,
)
from apps.engine.killstats.ingestion.repositories.killstats_repository import (
    KillStatsRepository,
)
from apps.engine.killstats.models.creature_spawn_event import CreatureSpawnEvent
from apps.engine.killstats.models.killstat import KillStat
from apps.engine.snapshots.models.snapshot import Snapshot
from apps.game_data.creatures.models.creature import Creature
from apps.game_data.worlds.models.world import World


@pytest.mark.django_db
class TestKillStatsRepository:

    def test_save_persists_all_fields_correctly(self) -> None:
        """
        Teste exaustivo: Garante que cada campo do DTO é mapeado para a
        coluna correta no banco de dados.
        """
        repo = KillStatsRepository()
        captured_at = datetime(2026, 4, 20, 19, 32, tzinfo=UTC)

        dto = WorldKillStatsDTO(
            snapshot_id="full_test_id",
            world_id="11",
            world_name="Auroria",
            captured_at=captured_at,
            data=[
                CreatureStatsDTO(
                    creature="Dragon Lord",
                    last_day=KillStatsMetricDTO(
                        players_killed=10, creatures_killed=200
                    ),
                    last_7_days=KillStatsMetricDTO(
                        players_killed=50, creatures_killed=1000
                    ),
                )
            ],
        )

        # Act
        snapshot = repo.save_world_kill_stats(dto, "auroria.json")

        # Assert - Tabela World
        assert snapshot.world.external_id == "11"
        assert snapshot.world.name == "auroria"  # Normalizado pelo Model

        # Assert - Tabela Snapshot
        assert snapshot.snapshot_id == "full_test_id"
        assert snapshot.captured_at == captured_at
        assert snapshot.source_file == "auroria.json"

        # Assert - Tabela KillStat (Mapeamento de métricas)
        killstat = KillStat.objects.get(snapshot=snapshot)
        assert killstat.creature.name == "dragon lord"
        assert killstat.last_day_players_killed == 10
        assert killstat.last_day_creatures_killed == 200
        assert killstat.last_7_days_players_killed == 50
        assert killstat.last_7_days_creatures_killed == 1000

    def test_atomic_rollback_on_unexpected_error(self) -> None:
        """
        Garante que se algo falhar no meio do bulk_create, o Snapshot e
        o World (se novo) não fiquem órfãos no banco.
        """
        repo = KillStatsRepository()
        dto = WorldKillStatsDTO(
            snapshot_id="error_test",
            world_id="12",
            world_name="Zuna",
            captured_at=datetime.now(UTC),
            data=[
                CreatureStatsDTO(
                    "Rat", KillStatsMetricDTO(0, 0), KillStatsMetricDTO(0, 0)
                )
            ],
        )

        # Simulamos uma falha forçada injetando um erro onde o Repo não espera
        # ou simplesmente interrompendo a transação.
        try:
            with transaction.atomic():
                repo.save_world_kill_stats(dto)
                # Forçamos um erro imediatamente após a chamada do repo
                raise RuntimeError("Falha simulada")
        except RuntimeError:
            pass

        # Verificação: O snapshot_id não deve existir pois houve rollback
        assert Snapshot.objects.filter(snapshot_id="error_test").exists() is False
        # O mundo Zuna também não deve existir (se foi criado na transação)
        assert World.objects.filter(name="zuna").exists() is False
        # Verificação Adicional: O evento também não deve existir
        assert CreatureSpawnEvent.objects.count() == 0

    def test_reuse_entities_prevents_duplication(self) -> None:
        """
        Garante que entidades mestre (World e Creature) não sejam duplicadas
        ao processar múltiplos snapshots para o mesmo cenário.
        """
        repo = KillStatsRepository()

        # --- PRIMEIRO PROCESSAMENTO ---
        dto_1 = WorldKillStatsDTO(
            snapshot_id="snapshot_monday",
            world_id="10",
            world_name="Antica",
            captured_at=datetime(2026, 4, 20, tzinfo=UTC),
            data=[
                CreatureStatsDTO(
                    "Dragon", KillStatsMetricDTO(1, 1), KillStatsMetricDTO(1, 1)
                )
            ],
        )
        repo.save_world_kill_stats(dto_1, "monday.json")

        # Verificação intermediária para garantir o estado inicial
        assert World.objects.count() == 1
        assert Creature.objects.count() == 1
        assert Snapshot.objects.count() == 1

        # --- SEGUNDO PROCESSAMENTO (Novo arquivo, mesmo mundo/criatura) ---
        dto_2 = WorldKillStatsDTO(
            snapshot_id="snapshot_tuesday",  # ID Diferente
            world_id="10",
            world_name="Antica",  # Mesmo Mundo
            captured_at=datetime(2026, 4, 21, tzinfo=UTC),
            data=[
                CreatureStatsDTO(
                    "Dragon", KillStatsMetricDTO(2, 2), KillStatsMetricDTO(2, 2)
                )
            ],  # Mesma criatura
        )
        repo.save_world_kill_stats(dto_2, "tuesday.json")

        # --- ASSERÇÕES FINAIS ---
        # As entidades mestre devem continuar sendo únicas
        assert World.objects.count() == 1
        assert Creature.objects.count() == 1

        # Os fatos (Snapshots e KillStats) devem ser dois
        assert Snapshot.objects.count() == 2, "Deve haver 2 snapshots distintos."
        assert (
            KillStat.objects.count() == 2
        ), "Deve haver 2 registros de estatísticas vinculados."

        # Verifica se cada KillStat aponta para o snapshot correto
        assert KillStat.objects.filter(snapshot__snapshot_id="snapshot_monday").exists()
        assert KillStat.objects.filter(
            snapshot__snapshot_id="snapshot_tuesday"
        ).exists()

    def test_multiple_creatures_in_single_snapshot(self) -> None:
        """Testa o comportamento do bulk_create com múltiplos registros."""
        repo = KillStatsRepository()
        dto = WorldKillStatsDTO(
            snapshot_id="multi_creature",
            world_id="1",
            world_name="Antica",
            captured_at=datetime.now(UTC),
            data=[
                CreatureStatsDTO(
                    "Rat", KillStatsMetricDTO(0, 0), KillStatsMetricDTO(0, 0)
                ),
                CreatureStatsDTO(
                    "Cave Rat", KillStatsMetricDTO(0, 0), KillStatsMetricDTO(0, 0)
                ),
            ],
        )

        repo.save_world_kill_stats(dto)

        assert (
            KillStat.objects.filter(snapshot__snapshot_id="multi_creature").count() == 2
        )
        assert Creature.objects.filter(name__in=["rat", "cave rat"]).count() == 2

    def test_save_world_kill_stats_creates_events(self) -> None:
        """
        Garante que um CreatureSpawnEvent é criado automaticamente quando
        há registro de criaturas mortas no DTO.
        """
        repo = KillStatsRepository()
        captured_at = datetime(2026, 4, 20, 19, 32, tzinfo=UTC)
        dto = WorldKillStatsDTO(
            snapshot_id="event_test",
            world_id="1",
            world_name="Antica",
            captured_at=captured_at,
            data=[
                CreatureStatsDTO(
                    creature="Orshabaal",
                    last_day=KillStatsMetricDTO(
                        players_killed=0, creatures_killed=1
                    ),  # Abate real
                    last_7_days=KillStatsMetricDTO(
                        players_killed=10, creatures_killed=20
                    ),
                )
            ],
        )

        repo.save_world_kill_stats(dto)

        # Assert - Evento de Spawn
        # O evento deve existir, ser um abate real (is_puff=False) e ter a data correta
        event = CreatureSpawnEvent.objects.get(creature__name="orshabaal")
        assert event.world.name == "antica"
        assert event.is_puff is False  # Regra: Ingestão JSON = Abate
        assert event.timestamp == captured_at
        assert event.reported_by is None  # Ingestão automática não tem usuário

    def test_save_does_not_create_event_when_no_kills(self) -> None:
        """
        Garante que NÃO é criado um CreatureSpawnEvent se creatures_killed for 0.
        """
        repo = KillStatsRepository()
        dto = WorldKillStatsDTO(
            snapshot_id="no_event_test",
            world_id="1",
            world_name="Antica",
            captured_at=datetime.now(UTC),
            data=[
                CreatureStatsDTO(
                    creature="Rat",
                    last_day=KillStatsMetricDTO(0, 0),  # Sem abates
                    last_7_days=KillStatsMetricDTO(0, 10),
                )
            ],
        )

        # Act
        repo.save_world_kill_stats(dto)

        # Assert
        assert CreatureSpawnEvent.objects.filter(creature__name="rat").exists() is False

    def test_unique_constraint_collision_per_day_and_world(self) -> None:
        """
        TESTE DE COLISÃO: Garante que o banco impede dois eventos para a
        mesma criatura, no mesmo dia e no mesmo mundo.
        """
        repo = KillStatsRepository()
        day_one = datetime(2026, 4, 20, 10, 0, tzinfo=UTC)
        day_one_later = datetime(
            2026, 4, 20, 22, 0, tzinfo=UTC
        )  # Mesmo dia, hora diferente

        dto1 = WorldKillStatsDTO(
            snapshot_id="snap_1",
            world_id="1",
            world_name="Antica",
            captured_at=day_one,
            data=[
                CreatureStatsDTO(
                    "Orshabaal", KillStatsMetricDTO(0, 1), KillStatsMetricDTO(0, 1)
                )
            ],
        )

        dto2 = WorldKillStatsDTO(
            snapshot_id="snap_2",
            world_id="1",
            world_name="Antica",
            captured_at=day_one_later,
            data=[
                CreatureStatsDTO(
                    "Orshabaal", KillStatsMetricDTO(0, 1), KillStatsMetricDTO(0, 1)
                )
            ],
        )

        # Primeiro salvamento OK
        repo.save_world_kill_stats(dto1)

        # Segundo salvamento deve falhar na constraint do banco
        with pytest.raises(IntegrityError):
            repo.save_world_kill_stats(dto2)
