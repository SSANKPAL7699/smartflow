# backend/models/vendor.py
# Pydantic model + SQLAlchemy table for LFA1 (Vendor Master)

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional
from backend.database import Base

# ── SQLAlchemy Model (Database Table) ────────────────────────
class VendorDB(Base):
    __tablename__ = "lfa1_vendors"

    LIFNR      = Column(String, primary_key=True, index=True)  # Vendor number
    NAME1      = Column(String, nullable=False)                 # Company name
    LAND1      = Column(String(3))                              # Country code
    ORT01      = Column(String)                                 # City
    PSTLZ      = Column(String)                                 # Postal code
    LIFSP      = Column(String, default="")                     # Blocked flag
    KTOKK      = Column(String)                                 # Account group
    CREATED_ON = Column(String)                                 # Creation date

    # Relationship → Purchase Orders
    purchase_orders = relationship("PurchaseOrderDB", back_populates="vendor")

# ── Pydantic Schemas (API Request/Response) ───────────────────
class VendorBase(BaseModel):
    LIFNR:      str
    NAME1:      str
    LAND1:      Optional[str] = None
    ORT01:      Optional[str] = None
    PSTLZ:      Optional[str] = None
    LIFSP:      Optional[str] = ""
    KTOKK:      Optional[str] = None
    CREATED_ON: Optional[str] = None

class VendorCreate(VendorBase):
    pass                        # Same fields for creation

class VendorResponse(VendorBase):
    is_blocked: bool = Field(default=False)

    @classmethod
    def from_db(cls, db_vendor):
        return cls(
            **{k: getattr(db_vendor, k) for k in VendorBase.model_fields},
            is_blocked=db_vendor.LIFSP == "X"   # X means blocked in SAP
        )

    class Config:
        from_attributes = True  # Allows reading from SQLAlchemy objects