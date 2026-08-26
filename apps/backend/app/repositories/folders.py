import uuid
from datetime import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement

from app.db.models.folders import Folder
from app.repositories.pagination import Page
from app.schemas.pagination import PageParams


class FolderRepository:
    """Pure data access for `folders` - no business rules, no HTTP concerns.

    Permission filtering (who may see which folder) is deliberately not done
    here: it belongs to a higher layer once `shares` is wired in, so this
    repository stays a simple, reusable building block.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, folder_id: uuid.UUID) -> Folder | None:
        return await self._session.get(Folder, folder_id)

    async def get_children(self, parent_id: uuid.UUID | None, page: PageParams) -> Page[Folder]:
        return await self._paginate(Folder.parent_id == parent_id, page)

    async def list_by_owner(self, owner_id: uuid.UUID, page: PageParams) -> Page[Folder]:
        return await self._paginate(Folder.owner_id == owner_id, page)

    async def get_root_folders_for_owner(self, owner_id: uuid.UUID, page: PageParams) -> Page[Folder]:
        """Top-level folders (`parent_id IS NULL`) *owned by this user only*.

        Not the same as `get_children(None, page)`, which has no owner filter
        at all and would list every user's root folders indiscriminately -
        fine for an internal building block, unsafe as "my root folders".
        """
        return await self._paginate(and_(Folder.parent_id.is_(None), Folder.owner_id == owner_id), page)

    async def create(self, *, name: str, parent_id: uuid.UUID | None, owner_id: uuid.UUID) -> Folder:
        folder = Folder(name=name, parent_id=parent_id, owner_id=owner_id)
        self._session.add(folder)
        await self._session.flush()
        return folder

    async def rename(self, folder: Folder, name: str) -> Folder:
        folder.name = name
        await self._session.flush()
        # `updated_at` is server-computed (onupdate=func.now()): after an
        # UPDATE flush its value is expired, not populated, so a later sync
        # attribute read (e.g. Pydantic's `model_validate`) blows up with
        # "MissingGreenlet" instead of lazy-loading it. Refresh now, while
        # still inside an awaitable context.
        await self._session.refresh(folder)
        return folder

    async def soft_delete(self, folder: Folder, *, deleted_at: datetime) -> None:
        folder.deleted_at = deleted_at
        await self._session.flush()
        await self._session.refresh(folder)

    async def get_descendant_ids(self, folder_id: uuid.UUID) -> list[uuid.UUID]:
        """Every descendant folder id at any depth (not including `folder_id`
        itself), via a recursive CTE - one round trip regardless of depth."""
        base = select(Folder.id, Folder.parent_id).where(Folder.parent_id == folder_id).cte(recursive=True)
        descendants = base.union_all(
            select(Folder.id, Folder.parent_id).join(base, Folder.parent_id == base.c.id)
        )
        result = await self._session.execute(select(descendants.c.id))
        return list(result.scalars().all())

    async def soft_delete_many(self, folder_ids: list[uuid.UUID], *, deleted_at: datetime) -> None:
        if not folder_ids:
            return
        # Loaded and mutated one by one - not a bulk Core UPDATE - so this
        # goes through the normal unit-of-work: any of these folders already
        # held elsewhere in this session (the identity map returns the same
        # Python object) sees `deleted_at` update immediately, no expiry or
        # refresh dance required.
        stmt = select(Folder).where(Folder.id.in_(folder_ids), Folder.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        for folder in result.scalars().all():
            folder.deleted_at = deleted_at
        await self._session.flush()

    async def _paginate(self, condition: ColumnElement[bool], page: PageParams) -> Page[Folder]:
        not_deleted = Folder.deleted_at.is_(None)

        count_stmt = select(func.count()).select_from(Folder).where(condition, not_deleted)
        total = (await self._session.execute(count_stmt)).scalar_one()

        # `.id` as a tiebreaker: `name` alone isn't unique, and without a
        # fully-deterministic order Postgres can return rows in a different
        # sequence between two pages of the same query - duplicates on one
        # page, gaps on another.
        items_stmt = (
            select(Folder)
            .where(condition, not_deleted)
            .order_by(Folder.name, Folder.id)
            .limit(page.limit)
            .offset(page.offset)
        )
        result = await self._session.execute(items_stmt)
        items = list(result.scalars().all())

        return Page(items=items, total=total, limit=page.limit, offset=page.offset)
