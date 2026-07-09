from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import ProgressItem
from app.schemas.common import ProgressStatus


class ProgressRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_for_roadmap(
        self,
        roadmap_id: str,
        phase_titles: list[str],
    ) -> list[ProgressItem]:
        items = [
            ProgressItem(
                roadmap_id=roadmap_id,
                title=title,
                item_type="phase",
                status=ProgressStatus.pending.value,
                sort_order=index,
            )
            for index, title in enumerate(phase_titles)
        ]
        self.session.add_all(items)
        await self.session.flush()
        return items

    async def list_by_roadmap(self, roadmap_id: str) -> list[ProgressItem]:
        result = await self.session.execute(
            select(ProgressItem)
            .where(ProgressItem.roadmap_id == roadmap_id)
            .order_by(ProgressItem.sort_order)
        )
        return list(result.scalars().all())

    async def update_status(
        self, *, roadmap_id: str, item_id: str, status: ProgressStatus
    ) -> ProgressItem:
        result = await self.session.execute(
            select(ProgressItem).where(
                ProgressItem.roadmap_id == roadmap_id,
                ProgressItem.id == item_id,
            )
        )
        item = result.scalar_one()
        item.status = status.value
        await self.session.flush()
        return item
