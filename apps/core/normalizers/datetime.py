from datetime import datetime

from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _


def normalize_datetime(value: str) -> datetime:
    dt = parse_datetime(value)

    if dt is None:
        raise ValueError(_("Datetime normalization failed"))

    return dt
