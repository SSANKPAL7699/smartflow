# backend/models/purchase_order.py
# Pydantic model + SQLAlchemy table for EKKO (Purchase Order Header)

from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from backend.database import Base

# ── SQLAlchemy Model ──────────────────────────────────────────
class PurchaseOrderDB(Base):
    __tablename__ = "ekko_purchase_orders"

    EBELN = Column(String, primary_key=True, index=True)  # PO number
    LIFNR = Column(String, ForeignKey("lfa1_vendors.LIFNR"), index=True)
    BSART = Column(String)                                # PO type
    BEDAT = Column(String)                                # PO date
    WAERS = Column(String)                                # Currency
    NETWR = Column(Float)                                 # Net value
    EKGRP = Column(String)                                # Purchasing group
    ZTERM = Column(String)                                # Payment terms
    STATUS = Column(String)                               # PO status

    # Relationships
    vendor   = relationship("VendorDB", back_populates="purchase_orders")
    invoices = relationship("InvoiceDB", back_populates="purchase_order")

# ── Pydantic Schemas ──────────────────────────────────────────
class PurchaseOrderBase(BaseModel):
    EBELN:  str
    LIFNR:  Optional[str] = None
    BSART:  Optional[str] = None
    BEDAT:  Optional[str] = None
    WAERS:  Optional[str] = None
    NETWR:  Optional[float] = None
    EKGRP:  Optional[str] = None
    ZTERM:  Optional[str] = None
    STATUS: Optional[str] = None

class PurchaseOrderCreate(PurchaseOrderBase):
    pass

class PurchaseOrderResponse(PurchaseOrderBase):
    po_type_label: Optional[str] = None

    @classmethod
    def from_db(cls, db_po):
        type_labels = {
            "NB":  "Standard PO",
            "ZUB": "Stock Transfer",
            "FO":  "Framework Order"
        }
        return cls(
            **{k: getattr(db_po, k) for k in PurchaseOrderBase.model_fields},
            po_type_label=type_labels.get(db_po.BSART, db_po.BSART)
        )

    class Config:
        from_attributes = True