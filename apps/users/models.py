from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Modelo de usuário customizado.
    Permite expansões futuras.
    """

    email = models.EmailField(_("email address"), unique=True)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        db_table = "auth_user"

    def __str__(self) -> str:
        return str(self.username)
