from django.test import SimpleTestCase
from ingestion.services.validators.strings import validate_string
from ingestion.services.validators.base import ValidationError


class ValidateStringTest(SimpleTestCase):

    def test_valid_string(self) -> None:
        validate_string("Dragon")

    def test_optional_none(self) -> None:
        validate_string(None, required=False)

    def test_empty_required(self) -> None:
        with self.assertRaises(ValidationError):
            validate_string("")

    def test_none_required(self) -> None:
        with self.assertRaises(ValidationError):
            validate_string(None)

    def test_not_string(self) -> None:
        with self.assertRaises(ValidationError):
            validate_string(123)