from abc import ABC, abstractmethod


class BaseProvider[Raw, Parsed](ABC):
    @abstractmethod
    def normalize_raw(self, data: Raw) -> Parsed:
        raise NotImplementedError
