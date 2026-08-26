from dataclasses import dataclass


@dataclass
class Page[T]:
    """Generic paginated result for the repository/service layers.

    Deliberately not a Pydantic model: items are usually raw ORM objects at
    this level, and the eventual API response uses its own schema built from
    them (e.g. `Page[FolderRead]`) - this one is an internal transport shape,
    not something serialized directly.
    """

    items: list[T]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        return self.offset + len(self.items) < self.total
