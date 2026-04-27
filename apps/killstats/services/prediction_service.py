from datetime import datetime
from typing import TypedDict

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.killstats.models.monster_spawn_event import MonsterSpawnEvent
from apps.monsters.models.monster import Monster
from apps.worlds.models.world import World


class PredictionStatus(models.TextChoices):
    """Enums para os estados de predição com suporte a tradução."""

    COLLECTING = "COLLECTING", _("Collecting Data")
    NO_CHANCE = "NO_CHANCE", _("No Chance")
    EXPECTED = "EXPECTED", _("Expected Soon")
    OVERDUE = "OVERDUE", _("Overdue")
    MISSING = "MISSING", _("Missing/Probable Puff")


class PredictionResult(TypedDict):
    """Estrutura de dados tipada para o retorno da predição."""

    last_spawn: datetime | None
    days_since_last: int
    min_interval: int | None
    max_interval: int | None
    chance_percentage: float
    status: str  # Label traduzido
    status_code: str  # Chave estável do Enum


class PredictionService:
    @classmethod
    def get_prediction(cls, monster: Monster, world: World) -> PredictionResult:
        """
        Calcula a predição de spawn baseada no histórico local e janelas globais.
        """
        last_event = cls._get_last_event(monster, world)
        metadata = getattr(monster, "metadata", None)

        min_days = metadata.min_interval if metadata else None
        max_days = metadata.max_interval if metadata else None

        # Cenário Cold Start: Sem histórico ou sem configuração manual
        if not last_event or min_days is None or max_days is None:
            return cls._build_result(
                event=last_event,
                min_d=min_days,
                max_d=max_days,
                chance=0.0,
                status=PredictionStatus.COLLECTING,
            )

        days_passed = (timezone.now() - last_event.timestamp).days

        status_code = cls._determine_status(days_passed, min_days, max_days)
        chance = cls._calculate_chance(days_passed, min_days, max_days)

        return cls._build_result(
            event=last_event,
            min_d=min_days,
            max_d=max_days,
            chance=chance,
            status=status_code,
            days_passed=days_passed,
        )

    @staticmethod
    def _get_last_event(monster: Monster, world: World) -> MonsterSpawnEvent | None:
        """Busca o evento mais recente de spawn."""
        return (
            MonsterSpawnEvent.objects.filter(monster=monster, world=world)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def _determine_status(days: int, min_d: int, max_d: int) -> PredictionStatus:
        """Lógica pura para definir o estado atual."""
        if days < min_d:
            return PredictionStatus.NO_CHANCE
        if min_d <= days <= max_d:
            return PredictionStatus.EXPECTED
        if days > (max_d * 1.2):
            return PredictionStatus.MISSING
        return PredictionStatus.OVERDUE

    @staticmethod
    def _calculate_chance(days: int, min_d: int, max_d: int) -> float:
        """
        Calcula a chance.
        Retorna 0% se estiver antes da janela ou se o boss estiver MISSING.
        """
        # Se entrar no critério de MISSING (mais de 20% além do máximo), chance é 0
        if days > (max_d * 1.2):
            return 0.0

        if days < min_d:
            return 0.0

        if days >= max_d:
            return 100.0

        # Ajuste +1 para que o início da janela (days == min_d) já tenha chance real
        actual_progress = (days - min_d) + 1
        total_window = (max_d - min_d) + 1

        chance = (actual_progress / total_window) * 100
        return round(min(chance, 100.0), 2)

    @staticmethod
    def _build_result(
        event: MonsterSpawnEvent | None,
        min_d: int | None,
        max_d: int | None,
        chance: float,
        status: PredictionStatus,
        days_passed: int = 0,
    ) -> PredictionResult:
        """Monta o DTO de resposta final."""
        return {
            "last_spawn": event.timestamp if event else None,
            "days_since_last": days_passed,
            "min_interval": min_d,
            "max_interval": max_d,
            "chance_percentage": chance,
            "status": str(status.label),
            "status_code": status.value,
        }
