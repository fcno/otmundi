from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

from apps.identity.users.forms.user_forms import CustomUserCreationForm


@ratelimit(key="ip", rate="5/m", block=True)  # type: ignore
@require_http_methods(["GET", "POST"])
def register_view(request: HttpRequest) -> HttpResponse:
    """
    View de cadastro de novos usuários.
    Implementação inicial sem lógica de roles (será adicionada no próximo passo).
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("killstats:boss_monitor")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def user_delete_view(request: HttpRequest) -> HttpResponse:
    """
    Exclusão lógica: desativa o usuário em vez de deletar os dados físicos.
    """
    if request.method == "POST":
        user = request.user
        user.is_active = False  # Exclusão lógica
        user.save()
        logout(request)
        return redirect("users:login")

    return render(request, "users/user_confirm_delete.html")
