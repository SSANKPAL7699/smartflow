from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.services.analytics import (
    get_executive_summary,
    get_vendor_analytics,
    get_po_analytics,
    get_invoice_analytics,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
async def executive_summary(db: AsyncSession = Depends(get_db)):
    return await get_executive_summary(db)

@router.get("/vendors")
async def vendor_analytics(db: AsyncSession = Depends(get_db)):
    return await get_vendor_analytics(db)

@router.get("/purchase-orders")
async def po_analytics(db: AsyncSession = Depends(get_db)):
    return await get_po_analytics(db)

@router.get("/invoices")
async def invoice_analytics(db: AsyncSession = Depends(get_db)):
    return await get_invoice_analytics(db)