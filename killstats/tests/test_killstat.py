import pytest
from django.db.utils import IntegrityError
from django.utils.timezone import now

from killstats.models.killstat import KillStat
from monsters.models.monster import Monster
from snapshots.models.snapshot import Snapshot
from worlds.models.world import World


@pytest.mark.django_db
def test_create_killstat() -> None:
    world = World.objects.create(external_id="22", name="Serenian")

    snapshot = Snapshot.objects.create(
        world=world,
        captured_at=now(),
        source_file="file.json",
    )

    monster = Monster.objects.create(name="Dragon")

    ks = KillStat.objects.create(
        snapshot=snapshot,
        monster=monster,
        last_day_players_killed=1,
        last_day_monsters_killed=10,
        last_7_days_players_killed=5,
        last_7_days_monsters_killed=50,
    )

    assert ks.snapshot == snapshot
    assert ks.monster == monster

    assert ks.last_day_players_killed == 1
    assert ks.last_day_monsters_killed == 10
    assert ks.last_7_days_players_killed == 5
    assert ks.last_7_days_monsters_killed == 50


@pytest.mark.django_db
def test_unique_snapshot_monster() -> None:
    world = World.objects.create(external_id="22", name="Serenian")

    snapshot = Snapshot.objects.create(
        world=world,
        captured_at=now(),
        source_file="file.json",
    )

    monster = Monster.objects.create(name="Dragon")

    KillStat.objects.create(
        snapshot=snapshot,
        monster=monster,
        last_day_players_killed=1,
        last_day_monsters_killed=10,
        last_7_days_players_killed=5,
        last_7_days_monsters_killed=50,
    )

    with pytest.raises(IntegrityError):
        KillStat.objects.create(
            snapshot=snapshot,
            monster=monster,
            last_day_players_killed=2,
            last_day_monsters_killed=20,
            last_7_days_players_killed=6,
            last_7_days_monsters_killed=60,
        )
