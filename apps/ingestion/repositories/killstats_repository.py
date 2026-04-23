from django.db import transaction

from apps.ingestion.dto import WorldKillStatsDTO
from apps.killstats.models.killstat import KillStat
from apps.monsters.models.monster import Monster
from apps.snapshots.models.snapshot import Snapshot
from apps.worlds.models.world import World


class KillStatsRepository:
    def save_world_kill_stats(
        self, dto: WorldKillStatsDTO, source_file: str = ""
    ) -> Snapshot:
        """
        Persiste um DTO de KillStats. Assume que a validação de unicidade
        do snapshot_id já foi realizada pelo Service.
        """
        with transaction.atomic():
            # 1. Recupera ou cria o Mundo (Normalização feita no Model)
            world, _ = World.objects.get_or_create(
                name=dto.world_name.lower(), defaults={"external_id": dto.world_id}
            )

            # 2. Cria o Snapshot
            snapshot = Snapshot.objects.create(
                snapshot_id=dto.snapshot_id,
                world=world,
                captured_at=dto.captured_at,
                source_file=source_file,
            )

            # 3. Preparação das estatísticas de monstros
            kill_stats_to_create = []

            for item in dto.data:
                # Recupera ou cria o monstro (Normalização feita no Model)
                monster, _ = Monster.objects.get_or_create(name=item.monster.lower())

                kill_stats_to_create.append(
                    KillStat(
                        snapshot=snapshot,
                        monster=monster,
                        last_day_players_killed=item.last_day.players_killed,
                        last_day_monsters_killed=item.last_day.monsters_killed,
                        last_7_days_players_killed=item.last_7_days.players_killed,
                        last_7_days_monsters_killed=item.last_7_days.monsters_killed,
                    )
                )

            # 4. Inserção em massa para performance otimizada
            KillStat.objects.bulk_create(kill_stats_to_create)

            return snapshot
