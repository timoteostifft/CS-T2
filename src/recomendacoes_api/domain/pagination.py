from dataclasses import dataclass

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


@dataclass(frozen=True)
class Page[T]:
    items: list[T]
    total: int
