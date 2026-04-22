from abc import ABC, abstractmethod
from typing import Any


class BaseProvider[T](ABC):
    @abstractmethod
    def normalize_raw(self, data: dict[str, Any]) -> T:
        raise NotImplementedError
