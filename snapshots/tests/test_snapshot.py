from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils.timezone import now

from snapshots.models.snapshot import Snapshot
from worlds.models.world import World


class SnapshotModelTest(TestCase):

    def setUp(self) -> None:
        self.world = World.objects.create(external_id="22", name="Serenian")

    def test_create_snapshot(self) -> None:
        snapshot = Snapshot.objects.create(
            snapshot_id="snap1",
            world=self.world,
            captured_at=now(),
            source_file="file.json",
        )

        self.assertEqual(snapshot.world.name, "Serenian")

    def test_unique_snapshot_id(self) -> None:
        Snapshot.objects.create(
            snapshot_id="snap1",
            world=self.world,
            captured_at=now(),
            source_file="file.json",
        )

        with self.assertRaises(IntegrityError):
            Snapshot.objects.create(
                snapshot_id="snap1",
                world=self.world,
                captured_at=now(),
                source_file="file2.json",
            )
