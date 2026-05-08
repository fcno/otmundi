from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse


@login_required
def toggle_monster_preference(request: HttpRequest) -> HttpResponse:
    # Lógica temporária para não quebrar o sistema
    return HttpResponse("Em desenvolvimento")
