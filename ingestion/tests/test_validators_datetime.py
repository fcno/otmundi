from django.test import SimpleTestCase
from ingestion.services.validators.datetime import validate_datetime
from ingestion.services.validators.base import ValidationError


class ValidateDatetimeTest(SimpleTestCase):

    def test_valid_iso(self) -> None:
        validate_datetime("2026-04-18T17:00:00Z")

    def test_invalid_format(self) -> None:
        with self.assertRaises(ValidationError):
            validate_datetime("18/04/2026")

    def test_invalid_string(self) -> None:
        with self.assertRaises(ValidationError):
            validate_datetime("abc")

    def test_not_string(self) -> None:
        with self.assertRaises(ValidationError):
            validate_datetime(123)