from collections.abc import Callable, Iterable


def validate_and_normalize[T, R](
    value: T,
    validators: Iterable[Callable[[T], None]],
    normalizer: Callable[[T], R],
) -> R:
    for validator in validators:
        validator(value)
    return normalizer(value)
