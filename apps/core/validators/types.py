from typing import Protocol


class Validator(Protocol):
    def __call__(self, value: object) -> None: ...
