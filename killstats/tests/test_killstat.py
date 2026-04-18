from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils.timezone import now

from killstats.models.killstat import KillStat
from monsters.models.monster import Monster
from snapshots.models.snapshot import Snapshot
from worlds.models.world import World


class KillStatModelTest(TestCase):

    def setUp(self) -> None:
        self.world = World.objects.create(external_id="22", name="Serenian")

        self.snapshot = Snapshot.objects.create(
            snapshot_id="snap1",
            world=self.world,
            captured_at=now(),
            source_file="file.json",
        )

        self.monster = Monster.objects.create(name="Dragon")

    def test_create_killstat(self) -> None:
        ks = KillStat.objects.create(
            snapshot=self.snapshot,
            monster=self.monster,
            last_day_players_killed=1,
            last_day_monsters_killed=10,
            last_7_days_players_killed=5,
            last_7_days_monsters_killed=50,
        )

        self.assertEqual(ks.monster.name, "Dragon")
        self.assertEqual(ks.last_7_days_monsters_killed, 50)

    def test_unique_snapshot_monster(self) -> None:
        KillStat.objects.create(
            snapshot=self.snapshot,
            monster=self.monster,
            last_day_players_killed=1,
            last_day_monsters_killed=10,
            last_7_days_players_killed=5,
            last_7_days_monsters_killed=50,
        )

        with self.assertRaises(IntegrityError):
            KillStat.objects.create(
                snapshot=self.snapshot,
                monster=self.monster,
                last_day_players_killed=2,
                last_day_monsters_killed=20,
                last_7_days_players_killed=6,
                last_7_days_monsters_killed=60,
            )
