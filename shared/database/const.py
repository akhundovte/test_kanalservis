from enum import Enum


class _EnumWrap(Enum):
    @classmethod
    def get_values(cls):
        return list(map(lambda c: c.value, cls))

