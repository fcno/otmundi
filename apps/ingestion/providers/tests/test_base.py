# apps/ingestion/providers/tests/test_base.py
import pytest

from apps.ingestion.providers.base import BaseProvider


class DummyProvider(BaseProvider[int]):
    def normalize_raw(self, data: dict[str, object]) -> int:
        return 1


def test_base_provider_can_be_implemented() -> None:
    provider = DummyProvider()

    result = provider.normalize_raw({})

    assert result == 1


def test_base_provider_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        BaseProvider()
