from django.db.utils import IntegrityError
from django.test import TestCase

from worlds.models.world import World


class WorldModelTest(TestCase):

    def test_create_world(self) -> None:
        world = World.objects.create(external_id="22", name="Serenian")
        self.assertEqual(world.name, "Serenian")

    def test_unique_external_id(self) -> None:
        World.objects.create(external_id="22", name="A")
        with self.assertRaises(IntegrityError):
            World.objects.create(external_id="22", name="B")

    def test_unique_name(self) -> None:
        World.objects.create(external_id="22", name="Serenian")
        with self.assertRaises(IntegrityError):
            World.objects.create(external_id="23", name="Serenian")
