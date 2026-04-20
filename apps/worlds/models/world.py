from django.db import models


class World(models.Model):
    external_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150, unique=True)

    def __str__(self) -> str:
        return self.name
