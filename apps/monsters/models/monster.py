from typing import Any

from django.db import models


class Monster(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.name:
            self.name = self.name.lower().strip()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
