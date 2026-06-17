"""
Common schemas
"""
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Sayfa numarası")
    per_page: int = Field(default=20, ge=1, le=100, description="Sayfa başına öğe")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Sayfalanmış yanıt.
    Route'ların kullandığı (has_next/has_prev) ve frontend'in beklediği
    alanlarla uyumludur; per_page opsiyoneldir.
    """
    items: List[T]
    total: int
    page: int
    per_page: int = 0
    pages: int = 0
    has_next: bool = False
    has_prev: bool = False
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, per_page: int):
        pages = (total + per_page - 1) // per_page if per_page else 0
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1,
        )


class SuccessResponse(BaseModel):
    """Success response"""
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    message: str
    detail: Optional[Any] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    environment: str
