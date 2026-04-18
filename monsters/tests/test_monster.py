from django.db.utils import IntegrityError
from django.test import TestCase

from monsters.models.monster import Monster


class MonsterModelTest(TestCase):

    def test_create_monster(self) -> None:
        monster = Monster.objects.create(name="Dragon")
        self.assertEqual(monster.name, "Dragon")

    def test_unique_name(self) -> None:
        Monster.objects.create(name="Dragon")
        with self.assertRaises(IntegrityError):
            Monster.objects.create(name="Dragon")
