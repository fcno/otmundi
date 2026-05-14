from django.contrib.auth import views as auth_views
from django.urls import path

# Importação ajustada para o novo arquivo user_auth
from apps.identity.users.views.user_auth import register_view, user_delete_view

app_name = "users"

urlpatterns = [
    path("register/", register_view, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("delete/", user_delete_view, name="delete"),
    # As outras rotas de senha permanecem iguais...
]
