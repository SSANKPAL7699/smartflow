from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from backend.database import get_db
from backend.models.invoice import InvoiceDB, InvoiceResponse

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.get("/", response_model=list[InvoiceResponse])
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    status: Optional[str] = None,
    blocked: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(InvoiceDB)
    if status:
        query = query.where(InvoiceDB.RBSTAT == status.upper())
    if blocked is not None:
        query = query.where(InvoiceDB.ZLSPR == ("A" if blocked else ""))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    invoices = result.scalars().all()
    return [InvoiceResponse.from_db(i) for i in invoices]

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: str, db: AsyncSession = Depends(get_db)):
    invoice = await db.get(InvoiceDB, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
    return InvoiceResponse.from_db(invoice)