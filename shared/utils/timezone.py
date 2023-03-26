import pytz

from datetime import datetime
from shared.settings.config import TIME_ZONE


tzutc = pytz.utc
tzlocal = pytz.timezone(TIME_ZONE)
tzmoscow = pytz.timezone('Europe/Moscow')


def now_local_with_tz():
    return datetime.utcnow().replace(tzinfo=tzutc).astimezone(tzlocal)


def is_naive(value):
    """
    Determine if a given datetime.datetime is naive.
    The concept is defined in Python's docs:
    https://docs.python.org/library/datetime.html#datetime.tzinfo
    Assuming value.tzinfo is either None or a proper datetime.tzinfo,
    value.utcoffset() implements the appropriate logic.
    """
    return value.utcoffset() is None
