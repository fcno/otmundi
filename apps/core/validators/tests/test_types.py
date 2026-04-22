from apps.core.validators.types import Validator


def dummy_validator(value: object) -> None:
    pass


def test_validator_protocol_accepts_callable() -> None:
    v: Validator = dummy_validator
    v("any")  # não deve quebrar


def test_validator_protocol_type_check() -> None:
    v: Validator = dummy_validator
    v(123)
