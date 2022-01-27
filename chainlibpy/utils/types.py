from typing import Any


def is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
