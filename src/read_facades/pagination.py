from sqlalchemy import Select, select, func
from sqlalchemy.ext.asyncio import AsyncConnection
from dataclasses import dataclass
import math

from typing import TypeVar, Generic


T = TypeVar("T")

@dataclass
class Pagination:
    total_items : int
    total_pages : int
    items : list

async def paginate(query : Select, page : int, per_page : int, conn : AsyncConnection) -> Pagination:

    result = await conn.execute(query.limit(per_page).offset(page*per_page))
    total = (await conn.execute(select(func.count()).select_from(query.subquery()))).scalar()

    return Pagination(total_items=total, total_pages=math.ceil(total/per_page),items=result.unique().scalars().all())


@dataclass
class PaginatedDTO(Generic[T]):
    total_count : int
    total_page : int
    count : int
    page : int
    results : list[T]
