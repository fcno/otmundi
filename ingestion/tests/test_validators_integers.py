from django.test import SimpleTestCase
from ingestion.services.validators.integers import validate_integer
from ingestion.services.validators.base import ValidationError


class ValidateIntegerTest(SimpleTestCase):

    def test_valid_int(self) -> None:
        validate_integer(123)

    def test_valid_string_int(self) -> None:
        validate_integer("123")

    def test_invalid_with_spaces(self) -> None:
        with self.assertRaises(ValidationError):
            validate_integer(" 123 ")

    def test_invalid_with_thousand_separator_dot(self) -> None:
        with self.assertRaises(ValidationError):
            validate_integer("1.234")

    def test_invalid_with_comma(self) -> None:
        with self.assertRaises(ValidationError):
            validate_integer("1,234")

    def test_invalid_alpha(self) -> None:
        with self.assertRaises(ValidationError):
            validate_integer("abc")

    def test_none(self) -> None:
        with self.assertRaises(ValidationError):
            validate_integer(None)