from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from backend.database import get_db
from backend.models.purchase_order import PurchaseOrderDB, PurchaseOrderResponse

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])

@router.get("/", response_model=list[PurchaseOrderResponse])
async def get_purchase_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    status: Optional[str] = None,
    vendor_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(PurchaseOrderDB)
    if status:
        query = query.where(PurchaseOrderDB.STATUS == status.upper())
    if vendor_id:
        query = query.where(PurchaseOrderDB.LIFNR == vendor_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    pos = result.scalars().all()
    return [PurchaseOrderResponse.from_db(p) for p in pos]

@router.get("/{po_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(po_id: str, db: AsyncSession = Depends(get_db)):
    po = await db.get(PurchaseOrderDB, po_id)
    if not po:
        raise HTTPException(status_code=404, detail=f"Purchase Order {po_id} not found")
    return PurchaseOrderResponse.from_db(po)