from typing import cast

import pytest
from django.conf import LazySettings
from django.contrib.auth import get_user, get_user_model
from django.http import HttpResponseRedirect
from django.test import Client
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestUserViews:

    def test_register_view_success(self, client: Client) -> None:
        """Sucesso no cadastro e redirecionamento."""
        url = reverse("users:register")
        data = {
            "username": "newplayer",
            "email": "new@test.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert User.objects.filter(username="newplayer").exists()

    def test_registration_rate_limit(
        self, client: Client, settings: LazySettings
    ) -> None:
        """Caso de borda: Throttling de cadastro (Rate Limit)."""
        settings.RATELIMIT_ENABLE = True
        url = reverse("users:register")
        data = {"username": "flood", "password1": "p1", "password2": "p1"}

        # Simula 5 requisições rápidas
        for _ in range(5):
            client.post(url, data)

        # A 6ª deve ser bloqueada (403 se o block=True no decorator)
        response = client.post(url, data)
        assert response.status_code == 403

    def test_logical_delete_deactivates_user(self, client: Client) -> None:
        """Garante que a conta é desativada, não excluída fisicamente."""
        user = User.objects.create_user(username="bye", password="password123")
        client.force_login(user)

        url = reverse("users:delete")
        response = client.post(url)

        user.refresh_from_db()
        assert not user.is_active  # Exclusão lógica confirmada
        assert response.status_code == 302

        redirect_response = cast(HttpResponseRedirect, response)
        assert redirect_response.url == reverse("users:login")

    def test_inactive_user_cannot_login(self, client: Client) -> None:
        """Garante que usuário desativado não consegue se autenticar."""
        User.objects.create_user(
            username="inactive", password="password123", is_active=False
        )
        url = reverse("users:login")
        client.post(url, {"username": "inactive", "password": "password123"})

        user = get_user(client)

        # O Django não autentica is_active=False por padrão
        assert "_auth_user_id" not in client.session
        assert not user.is_authenticated  # Garante que é um AnonymousUser
