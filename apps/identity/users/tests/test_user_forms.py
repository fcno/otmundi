import pytest

from apps.identity.users.forms import CustomUserCreationForm
from apps.identity.users.models import User


@pytest.mark.django_db
class TestUserForms:
    def test_form_valid_data(self) -> None:
        """Sucesso com todos os campos obrigatórios."""
        data = {
            "username": "newplayer",
            "email": "player@otmundi.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        form = CustomUserCreationForm(data=data)
        assert form.is_valid()

    def test_form_passwords_dont_match(self) -> None:
        """Borda: Senhas diferentes devem invalidar o form."""
        data = {
            "username": "newplayer",
            "email": "player@otmundi.com",
            "password1": "Pass1",
            "password2": "Pass2",
        }
        form = CustomUserCreationForm(data=data)
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_form_invalid_email_format(self) -> None:
        """Borda: Formato de e-mail inválido."""
        data = {
            "username": "newplayer",
            "email": "not-an-email",
            "password1": "p",
            "password2": "p",
        }
        form = CustomUserCreationForm(data=data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_form_missing_required_fields(self) -> None:
        """Borda: Campos obrigatórios vazios."""
        form = CustomUserCreationForm(data={})
        assert not form.is_valid()
        assert "username" in form.errors
        assert "email" in form.errors

    def test_form_duplicate_email(self) -> None:
        """Caso de borda: Email já cadastrado."""
        User.objects.create_user(username="u1", email="same@test.com", password="p")
        data = {
            "username": "u2",
            "email": "same@test.com",
            "password1": "p",
            "password2": "p",
        }
        form = CustomUserCreationForm(data=data)
        assert not form.is_valid()
        assert "email" in form.errors
