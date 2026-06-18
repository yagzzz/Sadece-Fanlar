"""
Şikayet/Rapor sistemi — kullanıcılar içerik/kullanıcı bildirir, moderatörler işler.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.admin import Report, ReportType, ReportStatus
from app.api.deps import get_current_user, get_staff_user

router = APIRouter(prefix="/reports", tags=["Reports"])


class ReportCreate(BaseModel):
    reported_type: str = Field(..., description="post | user | message | comment")
    reported_id: UUID
    type: ReportType = ReportType.OTHER
    description: str = Field("", max_length=2000)
    reported_user_id: Optional[UUID] = None


@router.post("")
async def create_report(
    data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """İçerik veya kullanıcı şikayeti oluştur (AI/sahte içerik dahil)."""
    report = Report(
        reporter_id=current_user.id,
        reported_type=data.reported_type,
        reported_id=data.reported_id,
        reported_user_id=data.reported_user_id,
        type=data.type,
        description=data.description or "",
        status=ReportStatus.PENDING,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return {"id": str(report.id), "status": report.status.value, "message": "Şikayetiniz alındı, ekibimiz inceleyecek."}


@router.get("/queue")
async def report_queue(
    status_filter: Optional[ReportStatus] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    staff: User = Depends(get_staff_user),
    db: AsyncSession = Depends(get_db),
):
    """Moderatör/admin: şikayet kuyruğu."""
    query = select(Report)
    if status_filter:
        query = query.where(Report.status == status_filter)
    else:
        query = query.where(Report.status.in_([ReportStatus.PENDING, ReportStatus.REVIEWING]))

    total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0
    query = query.order_by(Report.created_at.desc()).offset((page - 1) * limit).limit(limit)
    rows = (await db.execute(query)).scalars().all()

    items = [
        {
            "id": str(r.id),
            "reporter_id": str(r.reporter_id),
            "reported_type": r.reported_type,
            "reported_id": str(r.reported_id),
            "reported_user_id": str(r.reported_user_id) if r.reported_user_id else None,
            "type": r.type.value if hasattr(r.type, "value") else r.type,
            "description": r.description,
            "status": r.status.value if hasattr(r.status, "value") else r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
    return {"items": items, "total": total, "page": page, "limit": limit}


class ReportResolve(BaseModel):
    status: ReportStatus = ReportStatus.RESOLVED
    resolution_note: str = ""
    action_taken: Optional[str] = None


@router.post("/{report_id}/resolve")
async def resolve_report(
    report_id: UUID,
    data: ReportResolve,
    staff: User = Depends(get_staff_user),
    db: AsyncSession = Depends(get_db),
):
    """Moderatör/admin: şikayeti sonuçlandır."""
    report = (await db.execute(select(Report).where(Report.id == report_id))).scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Şikayet bulunamadı")

    report.status = data.status
    report.resolution_note = data.resolution_note
    report.action_taken = data.action_taken
    report.reviewed_by_id = staff.id
    report.reviewed_at = datetime.utcnow()
    await db.commit()
    return {"id": str(report.id), "status": report.status.value}
