from typing import Any

from django.contrib.auth.models import AbstractUser, Group
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Modelo de usuário customizado com hierarquia de Roles e integração com Grupos.
    """

    email = models.EmailField(_("email address"), unique=True)

    class Role(models.IntegerChoices):
        PLAYER = 10, _("Player")
        TUTOR = 20, _("Tutor")
        SENIOR_TUTOR = 30, _("Senior Tutor")
        GAMEMASTER = 40, _("GameMaster")
        COMMUNITY_MANAGER = 50, _("Community Manager")
        ADMIN = 60, _("Administrator")

    role = models.SmallIntegerField(
        choices=Role.choices, default=Role.PLAYER, verbose_name=_("Role")
    )

    class Meta:
        app_label = "users"
        verbose_name = _("user")
        verbose_name_plural = _("users")
        db_table = "auth_user"

    def __str__(self) -> str:
        return _("{username} ({role})").format(
            username=self.username, role=self.get_role_display()
        )

    def sync_role_to_group(self) -> None:
        """
        Sincroniza a Role numérica com os Grupos de Permissão do Django.
        Isso permite gerenciar permissões N:M via Banco de Dados.
        """
        group_name = self.get_role_display()
        group, _ = Group.objects.get_or_create(name=group_name)

        with transaction.atomic():
            self.groups.clear()
            self.groups.add(group)

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        # Sincroniza sempre que for salvo para garantir integridade Role <-> Group
        self.sync_role_to_group()
