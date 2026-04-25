from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from backend.database import get_db
from backend.models.vendor import VendorDB, VendorResponse

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.get("/", response_model=list[VendorResponse])
async def get_vendors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    country: Optional[str] = None,
    blocked: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(VendorDB)
    if country:
        query = query.where(VendorDB.LAND1 == country.upper())
    if blocked is not None:
        query = query.where(VendorDB.LIFSP == ("X" if blocked else ""))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    vendors = result.scalars().all()
    return [VendorResponse.from_db(v) for v in vendors]

@router.get("/stats/summary")
async def get_vendor_summary(db: AsyncSession = Depends(get_db)):
    total = await db.execute(select(func.count()).select_from(VendorDB))
    blocked = await db.execute(
        select(func.count()).select_from(VendorDB).where(VendorDB.LIFSP == "X")
    )
    return {"total_vendors": total.scalar(), "blocked_vendors": blocked.scalar()}

@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: str, db: AsyncSession = Depends(get_db)):
    vendor = await db.get(VendorDB, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail=f"Vendor {vendor_id} not found")
    return VendorResponse.from_db(vendor)