# backend/models/invoice.py
# Pydantic model + SQLAlchemy table for RBKP (Invoice Header)

from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from backend.database import Base

# ── SQLAlchemy Model ──────────────────────────────────────────
class InvoiceDB(Base):
    __tablename__ = "rbkp_invoices"

    BELNR  = Column(String, primary_key=True, index=True)  # Invoice number
    EBELN  = Column(String, ForeignKey("ekko_purchase_orders.EBELN"), index=True)
    BLDAT  = Column(String)                                 # Invoice date
    WAERS  = Column(String)                                 # Currency
    RMWWR  = Column(Float)                                  # Gross amount
    WMWST  = Column(Float)                                  # Tax amount
    NETWR  = Column(Float)                                  # Net amount
    ZLSPR  = Column(String, default="")                     # Payment block
    RBSTAT = Column(String)                                 # Invoice status

    # Relationship
    purchase_order = relationship("PurchaseOrderDB", back_populates="invoices")

# ── Pydantic Schemas ──────────────────────────────────────────
class InvoiceBase(BaseModel):
    BELNR:  str
    EBELN:  Optional[str] = None
    BLDAT:  Optional[str] = None
    WAERS:  Optional[str] = None
    RMWWR:  Optional[float] = None
    WMWST:  Optional[float] = None
    NETWR:  Optional[float] = None
    ZLSPR:  Optional[str] = ""
    RBSTAT: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceResponse(InvoiceBase):
    is_payment_blocked: bool = False
    tax_rate: Optional[float] = None

    @classmethod
    def from_db(cls, db_inv):
        tax_rate = None
        if db_inv.RMWWR and db_inv.RMWWR > 0:
            tax_rate = round((db_inv.WMWST / db_inv.RMWWR) * 100, 2)
        return cls(
            **{k: getattr(db_inv, k) for k in InvoiceBase.model_fields},
            is_payment_blocked=db_inv.ZLSPR == "A",
            tax_rate=tax_rate
        )

    class Config:
        from_attributes = True