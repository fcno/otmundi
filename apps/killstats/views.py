from django.views.generic import ListView
from apps.monsters.models.monster import Monster
from apps.worlds.models.world import World
from .services.prediction_service import PredictionService

class BossMonitorView(ListView):
    model = Monster
    template_name = "monitor.html"
    context_object_name = "bosses"

    def get_queryset(self):
        """
        Retorna apenas monstros que possuem metadados configurados (bosses),
        já trazendo os metadados para evitar múltiplas consultas ao banco (N+1).
        """
        return Monster.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Identifica o mundo (pode ser expandido para filtros via URL futuramente)
        # Por padrão, pegamos o primeiro mundo cadastrado
        world = World.objects.first() 
        
        if not world:
            context['prediction_enabled'] = False
            return context

        # 2. Injeta a predição em cada objeto boss no contexto
        # O PredictionService processa o histórico e devolve o status e a chance
        for boss in context['bosses']:
            boss.prediction = PredictionService.get_prediction(boss, world)
        
        context['current_world'] = world
        context['prediction_enabled'] = True
        return context
