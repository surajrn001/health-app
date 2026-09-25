from typing import Generic, List, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class PaginationMeta(BaseModel):
    total_items: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    meta: PaginationMeta
