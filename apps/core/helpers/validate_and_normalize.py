from typing import Callable, Iterable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def validate_and_normalize(
    value: T,
    validators: Iterable[Callable[[T], None]],
    normalizer: Callable[[T], R],
) -> R:
    for validator in validators:
        validator(value)
    return normalizer(value)