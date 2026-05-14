from django.contrib.auth.forms import UserCreationForm

from apps.identity.users.models import User


class CustomUserCreationForm(UserCreationForm[User]):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
