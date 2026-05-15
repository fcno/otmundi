import pytest
from django.db.utils import IntegrityError
from django.utils.timezone import now

from apps.engine.killstats.models import KillStat
from apps.engine.killstats.models.creature_config import CreatureConfig
from apps.engine.snapshots.models import Snapshot
from apps.game_data.creatures.models import Creature
from apps.game_data.worlds.models import World


@pytest.mark.django_db
def test_create_killstat() -> None:
    world = World.objects.create(external_id="22", name="Serenian")

    snapshot = Snapshot.objects.create(
        world=world,
        captured_at=now(),
        source_file="file.json",
    )

    creature = Creature.objects.create(name="Dragon")
    CreatureConfig.objects.create(creature=creature, is_active=True)

    ks = KillStat.objects.create(
        snapshot=snapshot,
        creature=creature,
        last_day_players_killed=1,
        last_day_creatures_killed=10,
        last_7_days_players_killed=5,
        last_7_days_creatures_killed=50,
    )

    assert ks.snapshot == snapshot
    assert ks.creature == creature

    assert ks.last_day_players_killed == 1
    assert ks.last_day_creatures_killed == 10
    assert ks.last_7_days_players_killed == 5
    assert ks.last_7_days_creatures_killed == 50


@pytest.mark.django_db
def test_unique_snapshot_creature() -> None:
    world = World.objects.create(external_id="22", name="Serenian")

    snapshot = Snapshot.objects.create(
        world=world,
        captured_at=now(),
        source_file="file.json",
    )

    creature = Creature.objects.create(name="Dragon")
    CreatureConfig.objects.create(creature=creature, is_active=True)

    KillStat.objects.create(
        snapshot=snapshot,
        creature=creature,
        last_day_players_killed=1,
        last_day_creatures_killed=10,
        last_7_days_players_killed=5,
        last_7_days_creatures_killed=50,
    )

    with pytest.raises(IntegrityError):
        KillStat.objects.create(
            snapshot=snapshot,
            creature=creature,
            last_day_players_killed=2,
            last_day_creatures_killed=20,
            last_7_days_players_killed=6,
            last_7_days_creatures_killed=60,
        )
