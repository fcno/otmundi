from datetime import datetime
from django.utils.dateparse import parse_datetime


def normalize_datetime(value: str) -> datetime:
    return parse_datetime(value)