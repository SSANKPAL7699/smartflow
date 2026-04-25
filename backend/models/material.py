# backend/models/material.py
# Pydantic model + SQLAlchemy table for MARA (Material Master)

from sqlalchemy import Column, String, Float
from pydantic import BaseModel
from typing import Optional
from backend.database import Base

# ── SQLAlchemy Model ──────────────────────────────────────────
class MaterialDB(Base):
    __tablename__ = "mara_materials"

    MATNR      = Column(String, primary_key=True, index=True)  # Material number
    MAKTX      = Column(String)                                 # Description
    MTART      = Column(String)                                 # Material type
    MEINS      = Column(String)                                 # Unit of measure
    MATKL      = Column(String)                                 # Material group
    NTGEW      = Column(Float)                                  # Net weight
    GEWEI      = Column(String)                                 # Weight unit
    CREATED_ON = Column(String)

# ── Pydantic Schemas ──────────────────────────────────────────
class MaterialBase(BaseModel):
    MATNR:      str
    MAKTX:      Optional[str] = None
    MTART:      Optional[str] = None
    MEINS:      Optional[str] = None
    MATKL:      Optional[str] = None
    NTGEW:      Optional[float] = None
    GEWEI:      Optional[str] = None
    CREATED_ON: Optional[str] = None

class MaterialCreate(MaterialBase):
    pass

class MaterialResponse(MaterialBase):
    material_type_label: Optional[str] = None

    @classmethod
    def from_db(cls, db_mat):
        # Convert SAP codes to readable labels
        type_labels = {
            "ROH":  "Raw Material",
            "HALB": "Semi-Finished",
            "FERT": "Finished Good",
            "HAWA": "Trading Good"
        }
        return cls(
            **{k: getattr(db_mat, k) for k in MaterialBase.model_fields},
            material_type_label=type_labels.get(db_mat.MTART, db_mat.MTART)
        )

    class Config:
        from_attributes = True