from pydantic import BaseModel, Field

from app.repositories.pagination import Page


class PageParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PageOut[T](BaseModel):
    """API-facing mirror of `Page[T]` - built from it at the router boundary,
    once ORM objects have been converted to their Pydantic `*Read` schema."""

    items: list[T]
    total: int
    limit: int
    offset: int
    has_more: bool

    @classmethod
    def from_page(cls, page: Page, item_type: type[T]) -> "PageOut[T]":
        return cls(
            items=[item_type.model_validate(item) for item in page.items],
            total=page.total,
            limit=page.limit,
            offset=page.offset,
            has_more=page.has_more,
        )
