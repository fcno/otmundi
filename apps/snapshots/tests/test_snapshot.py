import pytest
from django.db.utils import IntegrityError
from django.utils.timezone import now

from apps.snapshots.models.snapshot import Snapshot
from apps.worlds.models.world import World


@pytest.mark.django_db
def test_create_snapshot() -> None:
    world = World.objects.create(external_id="22", name="Serenian")
    ts = now()

    snapshot = Snapshot.objects.create(
        world=world,
        captured_at=ts,
        source_file="file.json",
    )

    assert snapshot.world == world
    assert snapshot.captured_at == ts
    assert snapshot.source_file == "file.json"


@pytest.mark.django_db
def test_unique_world_datetime() -> None:
    world = World.objects.create(external_id="22", name="Serenian")
    ts = now()

    Snapshot.objects.create(
        world=world,
        captured_at=ts,
        source_file="file.json",
    )

    with pytest.raises(IntegrityError):
        Snapshot.objects.create(
            world=world,
            captured_at=ts,
            source_file="file2.json",
        )
