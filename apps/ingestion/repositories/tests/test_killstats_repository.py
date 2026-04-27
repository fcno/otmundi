from datetime import UTC, datetime

import pytest
from django.db import transaction

from apps.ingestion.dto import KillStatsMetricDTO, MonsterStatsDTO, WorldKillStatsDTO
from apps.ingestion.repositories.killstats_repository import KillStatsRepository
from apps.killstats.models.killstat import KillStat
from apps.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.monsters.models.monster import Monster
from apps.snapshots.models.snapshot import Snapshot
from apps.worlds.models.world import World


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
                MonsterStatsDTO(
                    monster="Dragon Lord",
                    last_day=KillStatsMetricDTO(players_killed=10, monsters_killed=200),
                    last_7_days=KillStatsMetricDTO(
                        players_killed=50, monsters_killed=1000
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
        assert killstat.monster.name == "dragon lord"
        assert killstat.last_day_players_killed == 10
        assert killstat.last_day_monsters_killed == 200
        assert killstat.last_7_days_players_killed == 50
        assert killstat.last_7_days_monsters_killed == 1000

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
                MonsterStatsDTO(
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
        assert MonsterSpawnEvent.objects.count() == 0

    def test_reuse_entities_prevents_duplication(self) -> None:
        """
        Garante que entidades mestre (World e Monster) não sejam duplicadas
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
                MonsterStatsDTO(
                    "Dragon", KillStatsMetricDTO(1, 1), KillStatsMetricDTO(1, 1)
                )
            ],
        )
        repo.save_world_kill_stats(dto_1, "monday.json")

        # Verificação intermediária para garantir o estado inicial
        assert World.objects.count() == 1
        assert Monster.objects.count() == 1
        assert Snapshot.objects.count() == 1

        # --- SEGUNDO PROCESSAMENTO (Novo arquivo, mesmo mundo/monstro) ---
        dto_2 = WorldKillStatsDTO(
            snapshot_id="snapshot_tuesday",  # ID Diferente
            world_id="10",
            world_name="Antica",  # Mesmo Mundo
            captured_at=datetime(2026, 4, 21, tzinfo=UTC),
            data=[
                MonsterStatsDTO(
                    "Dragon", KillStatsMetricDTO(2, 2), KillStatsMetricDTO(2, 2)
                )
            ],  # Mesmo Monstro
        )
        repo.save_world_kill_stats(dto_2, "tuesday.json")

        # --- ASSERÇÕES FINAIS ---
        # As entidades mestre devem continuar sendo únicas
        assert World.objects.count() == 1
        assert Monster.objects.count() == 1

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

    def test_multiple_monsters_in_single_snapshot(self) -> None:
        """Testa o comportamento do bulk_create com múltiplos registros."""
        repo = KillStatsRepository()
        dto = WorldKillStatsDTO(
            snapshot_id="multi_monster",
            world_id="1",
            world_name="Antica",
            captured_at=datetime.now(UTC),
            data=[
                MonsterStatsDTO(
                    "Rat", KillStatsMetricDTO(0, 0), KillStatsMetricDTO(0, 0)
                ),
                MonsterStatsDTO(
                    "Cave Rat", KillStatsMetricDTO(0, 0), KillStatsMetricDTO(0, 0)
                ),
            ],
        )

        repo.save_world_kill_stats(dto)

        assert (
            KillStat.objects.filter(snapshot__snapshot_id="multi_monster").count() == 2
        )
        assert Monster.objects.filter(name__in=["rat", "cave rat"]).count() == 2

    def test_save_creates_spawn_event_on_kill(self) -> None:
        """
        Garante que um MonsterSpawnEvent é criado automaticamente quando
        há registro de monstros mortos no DTO.
        """
        repo = KillStatsRepository()
        captured_at = datetime(2026, 4, 25, tzinfo=UTC)

        dto = WorldKillStatsDTO(
            snapshot_id="event_generation_test",
            world_id="1",
            world_name="Antica",
            captured_at=captured_at,
            data=[
                MonsterStatsDTO(
                    monster="Orshabaal",
                    last_day=KillStatsMetricDTO(
                        players_killed=0, monsters_killed=1
                    ),  # Abate real
                    last_7_days=KillStatsMetricDTO(
                        players_killed=10, monsters_killed=20
                    ),
                )
            ],
        )

        # Act
        repo.save_world_kill_stats(dto)

        # Assert - Evento de Spawn
        # O evento deve existir, ser um abate real (is_puff=False) e ter a data correta
        event = MonsterSpawnEvent.objects.get(monster__name="orshabaal")
        assert event.is_puff is False  # Regra: Ingestão JSON = Abate
        assert event.timestamp.date() == captured_at.date()
        assert event.reported_by is None  # Ingestão automática não tem usuário

    def test_save_does_not_create_event_when_no_kills(self) -> None:
        """
        Garante que NÃO é criado um MonsterSpawnEvent se monsters_killed for 0.
        """
        repo = KillStatsRepository()
        dto = WorldKillStatsDTO(
            snapshot_id="no_event_test",
            world_id="1",
            world_name="Antica",
            captured_at=datetime.now(UTC),
            data=[
                MonsterStatsDTO(
                    monster="Rat",
                    last_day=KillStatsMetricDTO(0, 0),  # Sem abates
                    last_7_days=KillStatsMetricDTO(0, 10),
                )
            ],
        )

        # Act
        repo.save_world_kill_stats(dto)

        # Assert
        assert MonsterSpawnEvent.objects.filter(monster__name="rat").exists() is False
